"""
Conversation memory module for DockerForge AI assistant.

This module handles the storage and retrieval of conversation memory
for providing context-aware responses.
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np

from src.utils.logging_manager import get_logger

logger = get_logger("core.conversation_memory")


class ConversationMemoryManager:
    """
    Manager for conversation memory.
    
    This class handles the storage and retrieval of conversation memory
    for providing context-aware responses.
    """
    
    def __init__(self):
        """
        Initialize the conversation memory manager.
        """
        self.embedding_dimension = 768  # Default dimension for embeddings
        self.memory_limit = 50  # Maximum number of memories per user
        self.recency_weight = 0.3  # Weight for recency in importance score
        self.relevance_weight = 0.7  # Weight for relevance in importance score
        
    def add_memory(self, user_id: int, message_text: str, session_id: Optional[int] = None, 
                  message_id: Optional[int] = None, context: Optional[Dict[str, Any]] = None,
                  db_session=None) -> Dict[str, Any]:
        """
        Add a new memory entry for a user.
        
        Args:
            user_id: User ID
            message_text: Message text
            session_id: Optional session ID
            message_id: Optional message ID
            context: Optional context data
            db_session: Database session
            
        Returns:
            The created memory entry
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping memory creation")
                return {"success": False, "error": "No database session provided"}
            
            # Generate embedding
            embedding = self._generate_embedding(message_text)
            
            # Extract key information
            key_information = self._extract_key_information(message_text, context)
            
            # Calculate importance score
            importance_score = self._calculate_importance_score(message_text, context)
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ConversationMemory
            
            # Create memory entry
            memory_entry = ConversationMemory(
                user_id=user_id,
                session_id=session_id,
                message_id=message_id,
                embedding=embedding.tolist() if embedding is not None else None,
                key_information=key_information,
                importance_score=importance_score
            )
            
            # Add to database
            db_session.add(memory_entry)
            db_session.flush()
            
            # Prune old memories if needed
            self._prune_old_memories(user_id, db_session)
            
            return {
                "success": True,
                "memory_id": memory_entry.id,
                "importance_score": importance_score
            }
            
        except Exception as e:
            logger.error(f"Error adding memory: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_relevant_memories(self, user_id: int, query_text: str, 
                             context: Optional[Dict[str, Any]] = None,
                             limit: int = 5, db_session=None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for a user based on a query.
        
        Args:
            user_id: User ID
            query_text: Query text
            context: Optional context data
            limit: Maximum number of memories to return
            db_session: Database session
            
        Returns:
            List of relevant memory entries
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping memory retrieval")
                return []
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ConversationMemory
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query_text)
            
            if query_embedding is None:
                # Fall back to retrieving the most recent memories
                memories = db_session.query(ConversationMemory).filter(
                    ConversationMemory.user_id == user_id
                ).order_by(ConversationMemory.created_at.desc()).limit(limit).all()
                
                return [
                    {
                        "id": memory.id,
                        "key_information": memory.key_information,
                        "importance_score": memory.importance_score,
                        "created_at": memory.created_at.isoformat(),
                        "relevance_score": 0.0  # No relevance score available
                    }
                    for memory in memories
                ]
            
            # Get all memories for the user
            memories = db_session.query(ConversationMemory).filter(
                ConversationMemory.user_id == user_id
            ).all()
            
            # Calculate relevance scores
            memory_scores = []
            for memory in memories:
                if memory.embedding is not None:
                    memory_embedding = np.array(memory.embedding)
                    
                    # Calculate relevance using cosine similarity
                    similarity = self._calculate_similarity(query_embedding, memory_embedding)
                    
                    # Combine with importance score
                    combined_score = (
                        similarity * self.relevance_weight + 
                        memory.importance_score * self.recency_weight
                    )
                    
                    memory_scores.append({
                        "memory": memory,
                        "score": combined_score
                    })
            
            # Sort by combined score and take top N
            memory_scores.sort(key=lambda x: x["score"], reverse=True)
            top_memories = memory_scores[:limit]
            
            # Format results
            return [
                {
                    "id": item["memory"].id,
                    "key_information": item["memory"].key_information,
                    "importance_score": item["memory"].importance_score,
                    "created_at": item["memory"].created_at.isoformat(),
                    "relevance_score": item["score"]
                }
                for item in top_memories
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return []
    
    def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate an embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if generation fails
        """
        try:
            # In a real implementation, this would use a language model
            # to generate a proper embedding. For this prototype, we'll
            # use a simple random embedding.
            
            # Generate a random embedding for demonstration purposes
            embedding = np.random.rand(self.embedding_dimension)
            
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def _extract_key_information(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract key information from a message text and context.
        
        Args:
            text: Message text
            context: Optional context data
            
        Returns:
            Dictionary of key information
        """
        # In a real implementation, this would use NLP techniques to extract
        # key information from the text. For this prototype, we'll use a
        # simple approach.
        
        # Initialize key information
        key_info = {
            "topics": [],
            "entities": [],
            "intent": "unknown"
        }
        
        # Simple keyword matching for topics
        topics_keywords = {
            "container": ["container", "docker", "run", "start", "stop", "exec"],
            "image": ["image", "build", "pull", "push", "tag"],
            "volume": ["volume", "mount", "data", "persist"],
            "network": ["network", "connect", "disconnect", "bridge", "host"],
            "security": ["security", "vulnerability", "scan", "secure", "cve"],
            "troubleshooting": ["error", "issue", "problem", "fail", "debug", "troubleshoot"],
            "backup": ["backup", "restore", "export", "import", "save"],
            "configuration": ["config", "configure", "setup", "setting"]
        }
        
        # Check for topics
        text_lower = text.lower()
        for topic, keywords in topics_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                key_info["topics"].append(topic)
        
        # Simple intent detection
        if "?" in text:
            key_info["intent"] = "question"
        elif any(command in text_lower for command in ["start", "run", "create", "build", "deploy"]):
            key_info["intent"] = "command"
        elif any(keyword in text_lower for keyword in ["error", "issue", "problem", "fail", "help"]):
            key_info["intent"] = "help"
        
        # Add context information if available
        if context:
            if context.get("current_page"):
                key_info["page"] = context["current_page"]
            
            for context_key in ["current_container_id", "current_image_id", "vulnerability_id"]:
                if context.get(context_key):
                    key_info[context_key] = context[context_key]
        
        return key_info
    
    def _calculate_importance_score(self, text: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate an importance score for a message.
        
        Args:
            text: Message text
            context: Optional context data
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        # Initialize score
        score = 0.5  # Default mid-range score
        
        # Adjust based on message length (longer messages might be more informative)
        length_factor = min(len(text) / 500, 1.0) * 0.2
        score += length_factor
        
        # Adjust based on context
        if context:
            # Messages with specific context might be more important
            context_factor = min(len(context) / 5, 1.0) * 0.2
            score += context_factor
            
            # Specific contexts might be more important
            if context.get("vulnerability_id") or context.get("issue_id"):
                score += 0.2
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _prune_old_memories(self, user_id: int, db_session) -> None:
        """
        Prune old or less important memories to stay within the memory limit.
        
        Args:
            user_id: User ID
            db_session: Database session
        """
        try:
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ConversationMemory
            
            # Count memories for the user
            memory_count = db_session.query(ConversationMemory).filter(
                ConversationMemory.user_id == user_id
            ).count()
            
            # If we're over the limit, prune the least important ones
            if memory_count > self.memory_limit:
                # Get the least important memories
                excess_count = memory_count - self.memory_limit
                
                # Find IDs of memories to delete (least important first)
                to_delete = db_session.query(ConversationMemory.id).filter(
                    ConversationMemory.user_id == user_id
                ).order_by(ConversationMemory.importance_score.asc()).limit(excess_count).all()
                
                # Delete the memories
                if to_delete:
                    delete_ids = [id for (id,) in to_delete]
                    db_session.query(ConversationMemory).filter(
                        ConversationMemory.id.in_(delete_ids)
                    ).delete(synchronize_session=False)
                    
                    logger.info(f"Pruned {len(delete_ids)} old memories for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error pruning old memories: {str(e)}")


# Singleton instance
_conversation_memory_manager = None


def get_conversation_memory_manager() -> ConversationMemoryManager:
    """
    Get the conversation memory manager instance.
    
    Returns:
        The conversation memory manager instance
    """
    global _conversation_memory_manager
    if _conversation_memory_manager is None:
        _conversation_memory_manager = ConversationMemoryManager()
    return _conversation_memory_manager
