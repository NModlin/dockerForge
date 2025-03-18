"""
User preference manager for DockerForge AI assistant.

This module handles the storage and retrieval of user preferences
and the learning of user preferences over time.
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import Counter

from src.utils.logging_manager import get_logger

logger = get_logger("core.user_preference_manager")


class UserPreferenceManager:
    """
    Manager for user preferences.
    
    This class handles the storage and retrieval of user preferences
    and the learning of user preferences over time.
    """
    
    def __init__(self):
        """
        Initialize the user preference manager.
        """
        self.default_preferences = {
            "response_style": "balanced",
            "auto_suggestions": True,
            "preferred_topics": [],
            "avoided_topics": [],
            "feedback_preferences": {
                "topic_ratings": {},
                "positively_rated_responses": 0,
                "negatively_rated_responses": 0,
                "last_feedback_time": None
            }
        }
    
    def get_user_preferences(self, user_id: int, db_session=None) -> Dict[str, Any]:
        """
        Get preferences for a user.
        
        Args:
            user_id: User ID
            db_session: Database session
            
        Returns:
            User preferences
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, returning default preferences")
                return self.default_preferences.copy()
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import UserPreference
            
            # Get user preferences from database
            preferences = db_session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            # If no preferences found, create default preferences
            if preferences is None:
                preferences = UserPreference(
                    user_id=user_id,
                    response_style=self.default_preferences["response_style"],
                    auto_suggestions=self.default_preferences["auto_suggestions"],
                    preferred_topics=self.default_preferences["preferred_topics"],
                    avoided_topics=self.default_preferences["avoided_topics"],
                    feedback_preferences=self.default_preferences["feedback_preferences"]
                )
                db_session.add(preferences)
                db_session.commit()
            
            # Format preferences
            return {
                "id": preferences.id,
                "user_id": preferences.user_id,
                "response_style": preferences.response_style,
                "auto_suggestions": preferences.auto_suggestions,
                "preferred_topics": preferences.preferred_topics or [],
                "avoided_topics": preferences.avoided_topics or [],
                "feedback_preferences": preferences.feedback_preferences or self.default_preferences["feedback_preferences"],
                "created_at": preferences.created_at.isoformat(),
                "updated_at": preferences.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return self.default_preferences.copy()
    
    def update_user_preferences(self, user_id: int, preferences_data: Dict[str, Any], 
                               db_session=None) -> Dict[str, Any]:
        """
        Update preferences for a user.
        
        Args:
            user_id: User ID
            preferences_data: Preferences data to update
            db_session: Database session
            
        Returns:
            Updated user preferences
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping preference update")
                return {"success": False, "error": "No database session provided"}
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import UserPreference
            
            # Get user preferences from database
            preferences = db_session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            # If no preferences found, create default preferences
            if preferences is None:
                preferences = UserPreference(
                    user_id=user_id,
                    response_style=self.default_preferences["response_style"],
                    auto_suggestions=self.default_preferences["auto_suggestions"],
                    preferred_topics=self.default_preferences["preferred_topics"],
                    avoided_topics=self.default_preferences["avoided_topics"],
                    feedback_preferences=self.default_preferences["feedback_preferences"]
                )
                db_session.add(preferences)
            
            # Update preferences
            if "response_style" in preferences_data:
                preferences.response_style = preferences_data["response_style"]
            
            if "auto_suggestions" in preferences_data:
                preferences.auto_suggestions = preferences_data["auto_suggestions"]
            
            if "preferred_topics" in preferences_data:
                preferences.preferred_topics = preferences_data["preferred_topics"]
            
            if "avoided_topics" in preferences_data:
                preferences.avoided_topics = preferences_data["avoided_topics"]
            
            # Update timestamp
            preferences.updated_at = datetime.utcnow()
            
            # Commit changes
            db_session.commit()
            
            # Return updated preferences
            return {
                "success": True,
                "preferences": {
                    "id": preferences.id,
                    "user_id": preferences.user_id,
                    "response_style": preferences.response_style,
                    "auto_suggestions": preferences.auto_suggestions,
                    "preferred_topics": preferences.preferred_topics or [],
                    "avoided_topics": preferences.avoided_topics or [],
                    "feedback_preferences": preferences.feedback_preferences or self.default_preferences["feedback_preferences"],
                    "created_at": preferences.created_at.isoformat(),
                    "updated_at": preferences.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def process_message_feedback(self, user_id: int, message_id: int, rating: int, 
                                feedback_text: Optional[str] = None, db_session=None) -> Dict[str, Any]:
        """
        Process feedback on a message and update user preferences.
        
        Args:
            user_id: User ID
            message_id: Message ID
            rating: Rating (1-5)
            feedback_text: Optional feedback text
            db_session: Database session
            
        Returns:
            Result of feedback processing
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping feedback processing")
                return {"success": False, "error": "No database session provided"}
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import UserPreference, ChatMessage, ChatFeedback
            
            # Create feedback entry
            feedback = ChatFeedback(
                user_id=user_id,
                message_id=message_id,
                rating=rating,
                feedback_text=feedback_text
            )
            db_session.add(feedback)
            db_session.flush()
            
            # Get message to analyze content
            message = db_session.query(ChatMessage).filter(
                ChatMessage.id == message_id
            ).first()
            
            if message:
                # Get user preferences
                preferences = db_session.query(UserPreference).filter(
                    UserPreference.user_id == user_id
                ).first()
                
                # If no preferences found, create default preferences
                if preferences is None:
                    preferences = UserPreference(
                        user_id=user_id,
                        response_style=self.default_preferences["response_style"],
                        auto_suggestions=self.default_preferences["auto_suggestions"],
                        preferred_topics=self.default_preferences["preferred_topics"],
                        avoided_topics=self.default_preferences["avoided_topics"],
                        feedback_preferences=self.default_preferences["feedback_preferences"]
                    )
                    db_session.add(preferences)
                
                # Initialize feedback preferences if needed
                if preferences.feedback_preferences is None:
                    preferences.feedback_preferences = self.default_preferences["feedback_preferences"]
                
                # Extract topics from message
                topics = self._extract_topics(message.text)
                
                # Update topic ratings
                topic_ratings = preferences.feedback_preferences.get("topic_ratings", {})
                for topic in topics:
                    if topic not in topic_ratings:
                        topic_ratings[topic] = {"count": 0, "total_rating": 0, "avg_rating": 0}
                    
                    topic_ratings[topic]["count"] += 1
                    topic_ratings[topic]["total_rating"] += rating
                    topic_ratings[topic]["avg_rating"] = (
                        topic_ratings[topic]["total_rating"] / topic_ratings[topic]["count"]
                    )
                
                # Update rating counts
                if rating >= 4:
                    preferences.feedback_preferences["positively_rated_responses"] = (
                        preferences.feedback_preferences.get("positively_rated_responses", 0) + 1
                    )
                elif rating <= 2:
                    preferences.feedback_preferences["negatively_rated_responses"] = (
                        preferences.feedback_preferences.get("negatively_rated_responses", 0) + 1
                    )
                
                # Update timestamp
                preferences.feedback_preferences["last_feedback_time"] = datetime.utcnow().isoformat()
                preferences.feedback_preferences["topic_ratings"] = topic_ratings
                
                # Learn from feedback to update preferences
                self._learn_from_feedback(preferences, topics, rating)
                
                # Update timestamp
                preferences.updated_at = datetime.utcnow()
                
                # Commit changes
                db_session.commit()
                
                return {
                    "success": True,
                    "feedback_id": feedback.id,
                    "message": "Feedback processed and preferences updated"
                }
            else:
                db_session.commit()  # Still save the feedback
                return {
                    "success": True,
                    "feedback_id": feedback.id,
                    "message": "Feedback saved but message not found for preference learning"
                }
            
        except Exception as e:
            logger.error(f"Error processing message feedback: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_command_shortcuts(self, user_id: int, db_session=None) -> List[Dict[str, Any]]:
        """
        Get command shortcuts for a user.
        
        Args:
            user_id: User ID
            db_session: Database session
            
        Returns:
            List of command shortcuts
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, returning empty shortcuts list")
                return []
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ChatCommandShortcut
            
            # Get command shortcuts from database
            shortcuts = db_session.query(ChatCommandShortcut).filter(
                ChatCommandShortcut.user_id == user_id
            ).order_by(ChatCommandShortcut.usage_count.desc()).all()
            
            # Format shortcuts
            return [
                {
                    "id": shortcut.id,
                    "user_id": shortcut.user_id,
                    "command": shortcut.command,
                    "description": shortcut.description,
                    "template": shortcut.template,
                    "usage_count": shortcut.usage_count,
                    "created_at": shortcut.created_at.isoformat(),
                    "updated_at": shortcut.updated_at.isoformat()
                }
                for shortcut in shortcuts
            ]
            
        except Exception as e:
            logger.error(f"Error getting user command shortcuts: {str(e)}")
            return []
    
    def create_command_shortcut(self, user_id: int, command: str, description: str, 
                                template: str, db_session=None) -> Dict[str, Any]:
        """
        Create a new command shortcut for a user.
        
        Args:
            user_id: User ID
            command: Command (e.g., /logs)
            description: Description of what the command does
            template: Command template with placeholders
            db_session: Database session
            
        Returns:
            Created command shortcut
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping shortcut creation")
                return {"success": False, "error": "No database session provided"}
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ChatCommandShortcut
            
            # Check if command already exists for this user
            existing = db_session.query(ChatCommandShortcut).filter(
                ChatCommandShortcut.user_id == user_id,
                ChatCommandShortcut.command == command
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "error": f"Command {command} already exists for this user"
                }
            
            # Create command shortcut
            shortcut = ChatCommandShortcut(
                user_id=user_id,
                command=command,
                description=description,
                template=template,
                usage_count=0
            )
            db_session.add(shortcut)
            db_session.commit()
            
            # Return created shortcut
            return {
                "success": True,
                "shortcut": {
                    "id": shortcut.id,
                    "user_id": shortcut.user_id,
                    "command": shortcut.command,
                    "description": shortcut.description,
                    "template": shortcut.template,
                    "usage_count": shortcut.usage_count,
                    "created_at": shortcut.created_at.isoformat(),
                    "updated_at": shortcut.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating command shortcut: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def use_command_shortcut(self, user_id: int, command: str, db_session=None) -> Dict[str, Any]:
        """
        Record usage of a command shortcut and return its template.
        
        Args:
            user_id: User ID
            command: Command (e.g., /logs)
            db_session: Database session
            
        Returns:
            Command template
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping shortcut usage")
                return {"success": False, "error": "No database session provided"}
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ChatCommandShortcut
            
            # Get command shortcut from database
            shortcut = db_session.query(ChatCommandShortcut).filter(
                ChatCommandShortcut.user_id == user_id,
                ChatCommandShortcut.command == command
            ).first()
            
            if shortcut:
                # Increment usage count
                shortcut.usage_count += 1
                shortcut.updated_at = datetime.utcnow()
                db_session.commit()
                
                # Return template
                return {
                    "success": True,
                    "shortcut": {
                        "id": shortcut.id,
                        "command": shortcut.command,
                        "description": shortcut.description,
                        "template": shortcut.template,
                        "usage_count": shortcut.usage_count
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Command {command} not found for this user"
                }
            
        except Exception as e:
            logger.error(f"Error using command shortcut: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_command_shortcut(self, user_id: int, shortcut_id: int, db_session=None) -> Dict[str, Any]:
        """
        Delete a command shortcut for a user.
        
        Args:
            user_id: User ID
            shortcut_id: Shortcut ID
            db_session: Database session
            
        Returns:
            Result of deletion
        """
        try:
            # Skip if no database session
            if db_session is None:
                logger.warning("No database session provided, skipping shortcut deletion")
                return {"success": False, "error": "No database session provided"}
            
            # Import models within the function to avoid circular imports
            from src.web.api.models.chat import ChatCommandShortcut
            
            # Delete command shortcut
            result = db_session.query(ChatCommandShortcut).filter(
                ChatCommandShortcut.user_id == user_id,
                ChatCommandShortcut.id == shortcut_id
            ).delete()
            
            # Commit changes
            db_session.commit()
            
            if result:
                return {
                    "success": True,
                    "message": f"Command shortcut {shortcut_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Command shortcut {shortcut_id} not found for this user"
                }
            
        except Exception as e:
            logger.error(f"Error deleting command shortcut: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract topics from a message text.
        
        Args:
            text: Message text
            
        Returns:
            List of topics
        """
        # In a real implementation, this would use NLP techniques to extract
        # topics from the text. For this prototype, we'll use a simple approach.
        
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
        found_topics = []
        
        for topic, keywords in topics_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _learn_from_feedback(self, preferences, topics: List[str], rating: int) -> None:
        """
        Learn from feedback to update user preferences.
        
        Args:
            preferences: User preferences object
            topics: Topics in the message
            rating: Rating (1-5)
        """
        # Skip if no topics
        if not topics:
            return
        
        # Initialize preferred and avoided topics if needed
        if preferences.preferred_topics is None:
            preferences.preferred_topics = []
        
        if preferences.avoided_topics is None:
            preferences.avoided_topics = []
        
        # Update preferred topics based on high ratings
        if rating >= 4:
            for topic in topics:
                if topic not in preferences.preferred_topics and topic not in preferences.avoided_topics:
                    preferences.preferred_topics.append(topic)
        
        # Update avoided topics based on low ratings
        elif rating <= 2:
            for topic in topics:
                if topic in preferences.preferred_topics:
                    # Remove from preferred topics if low rated
                    preferences.preferred_topics.remove(topic)
                
                if topic not in preferences.avoided_topics:
                    # Only add to avoided topics if consistently low rated
                    topic_ratings = preferences.feedback_preferences.get("topic_ratings", {})
                    if topic in topic_ratings:
                        topic_data = topic_ratings[topic]
                        # Only add to avoided if we have multiple low ratings
                        if topic_data["count"] >= 3 and topic_data["avg_rating"] <= 2.5:
                            preferences.avoided_topics.append(topic)


# Singleton instance
_user_preference_manager = None


def get_user_preference_manager() -> UserPreferenceManager:
    """
    Get the user preference manager instance.
    
    Returns:
        The user preference manager instance
    """
    global _user_preference_manager
    if _user_preference_manager is None:
        _user_preference_manager = UserPreferenceManager()
    return _user_preference_manager
