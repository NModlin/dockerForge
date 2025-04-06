"""
Agent Memory for the Agent Framework

This module provides persistent memory and state management for agents,
enabling them to recall past interactions, store learned preferences,
and maintain context between executions.
"""

import json
import logging
import os
import pickle
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar, Union

logger = logging.getLogger(__name__)

# Type variables for generic methods
T = TypeVar("T")


class MemoryStore:
    """Base class for different types of agent memory stores"""

    def __init__(self, agent_id: str, name: str = "default"):
        self.agent_id = agent_id
        self.name = name

    def save(self, key: str, value: Any) -> None:
        """Save a value to memory"""
        raise NotImplementedError

    def load(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Load a value from memory"""
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """Delete a value from memory"""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if a key exists in memory"""
        raise NotImplementedError

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all keys in memory, optionally filtered by prefix"""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all values from memory"""
        raise NotImplementedError


class FileMemoryStore(MemoryStore):
    """Memory store that persists data to the file system"""

    def __init__(
        self, agent_id: str, name: str = "default", base_dir: Optional[str] = None
    ):
        super().__init__(agent_id, name)

        if base_dir is None:
            # Use a default location in the user's home directory
            base_dir = os.path.expanduser("~/.dockerforge/agent_memory")

        # Create directory if it doesn't exist
        self.agent_dir = os.path.join(base_dir, agent_id, name)
        os.makedirs(self.agent_dir, exist_ok=True)

        logger.debug(
            f"Initialized FileMemoryStore for agent {agent_id} at {self.agent_dir}"
        )

    def _get_path(self, key: str) -> str:
        """Get the file path for a key"""
        # Sanitize key to be a valid filename
        safe_key = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self.agent_dir, f"{safe_key}.pickle")

    def save(self, key: str, value: Any) -> None:
        """Save a value to a file"""
        path = self._get_path(key)
        try:
            with open(path, "wb") as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
            raise

    def load(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Load a value from a file"""
        path = self._get_path(key)
        if not os.path.exists(path):
            return default

        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading from memory: {e}")
            return default

    def delete(self, key: str) -> bool:
        """Delete a file"""
        path = self._get_path(key)
        if not os.path.exists(path):
            return False

        try:
            os.remove(path)
            return True
        except Exception as e:
            logger.error(f"Error deleting from memory: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a file exists"""
        path = self._get_path(key)
        return os.path.exists(path)

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List keys based on filenames"""
        if not os.path.exists(self.agent_dir):
            return []

        files = os.listdir(self.agent_dir)
        keys = [os.path.splitext(f)[0] for f in files if f.endswith(".pickle")]

        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]

        return keys

    def clear(self) -> None:
        """Delete all files in the directory"""
        if not os.path.exists(self.agent_dir):
            return

        for key in self.list_keys():
            self.delete(key)


class SQLiteMemoryStore(MemoryStore):
    """Memory store that persists data to a SQLite database"""

    def __init__(
        self, agent_id: str, name: str = "default", db_path: Optional[str] = None
    ):
        super().__init__(agent_id, name)

        if db_path is None:
            # Use a default location
            base_dir = os.path.expanduser("~/.dockerforge/agent_memory")
            os.makedirs(base_dir, exist_ok=True)
            db_path = os.path.join(base_dir, "memory.db")

        self.db_path = db_path

        # Initialize database
        self._init_db()

        logger.debug(f"Initialized SQLiteMemoryStore for agent {agent_id} in {db_path}")

    def _init_db(self) -> None:
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS memory (
            agent_id TEXT NOT NULL,
            store_name TEXT NOT NULL,
            key TEXT NOT NULL,
            value BLOB NOT NULL,
            updated_at INTEGER NOT NULL,
            PRIMARY KEY (agent_id, store_name, key)
        )
        """
        )

        # Create index for faster lookups
        cursor.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_memory_lookup
        ON memory (agent_id, store_name)
        """
        )

        conn.commit()
        conn.close()

    def save(self, key: str, value: Any) -> None:
        """Save a value to the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Serialize the value
            binary_data = pickle.dumps(value)

            # Insert or replace the value
            cursor.execute(
                """
            INSERT OR REPLACE INTO memory
            (agent_id, store_name, key, value, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
                (self.agent_id, self.name, key, binary_data, int(time.time())),
            )

            conn.commit()
        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def load(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Load a value from the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Query the value
            cursor.execute(
                """
            SELECT value FROM memory
            WHERE agent_id = ? AND store_name = ? AND key = ?
            """,
                (self.agent_id, self.name, key),
            )

            row = cursor.fetchone()
            if row is None:
                return default

            # Deserialize the value
            return pickle.loads(row[0])

        except Exception as e:
            logger.error(f"Error loading from memory: {e}")
            return default
        finally:
            conn.close()

    def delete(self, key: str) -> bool:
        """Delete a value from the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Delete the value
            cursor.execute(
                """
            DELETE FROM memory
            WHERE agent_id = ? AND store_name = ? AND key = ?
            """,
                (self.agent_id, self.name, key),
            )

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error deleting from memory: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def exists(self, key: str) -> bool:
        """Check if a key exists in the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Query the key
            cursor.execute(
                """
            SELECT 1 FROM memory
            WHERE agent_id = ? AND store_name = ? AND key = ?
            """,
                (self.agent_id, self.name, key),
            )

            return cursor.fetchone() is not None

        except Exception as e:
            logger.error(f"Error checking existence in memory: {e}")
            return False
        finally:
            conn.close()

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all keys for the agent"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            if prefix:
                # Query keys with prefix
                cursor.execute(
                    """
                SELECT key FROM memory
                WHERE agent_id = ? AND store_name = ? AND key LIKE ?
                ORDER BY key
                """,
                    (self.agent_id, self.name, f"{prefix}%"),
                )
            else:
                # Query all keys
                cursor.execute(
                    """
                SELECT key FROM memory
                WHERE agent_id = ? AND store_name = ?
                ORDER BY key
                """,
                    (self.agent_id, self.name),
                )

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error listing keys in memory: {e}")
            return []
        finally:
            conn.close()

    def clear(self) -> None:
        """Clear all values for the agent"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Delete all values
            cursor.execute(
                """
            DELETE FROM memory
            WHERE agent_id = ? AND store_name = ?
            """,
                (self.agent_id, self.name),
            )

            conn.commit()

        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            conn.rollback()
        finally:
            conn.close()


class MemoryEntry:
    """A single memory entry with metadata"""

    def __init__(
        self,
        content: Any,
        tags: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.tags = tags or []
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "content": self.content,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary representation"""
        return cls(
            content=data["content"],
            tags=data.get("tags", []),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if "timestamp" in data
                else None
            ),
            metadata=data.get("metadata", {}),
        )


class AgentMemory:
    """
    Memory manager for agents that provides persistent state, episodic memory,
    and semantic memory capabilities.
    """

    def __init__(self, agent_id: str, store_type: str = "sqlite"):
        self.agent_id = agent_id

        # Create different memory stores for different types of data
        if store_type == "file":
            self.state_store = FileMemoryStore(agent_id, "state")
            self.episodic_store = FileMemoryStore(agent_id, "episodic")
            self.semantic_store = FileMemoryStore(agent_id, "semantic")
        elif store_type == "sqlite":
            self.state_store = SQLiteMemoryStore(agent_id, "state")
            self.episodic_store = SQLiteMemoryStore(agent_id, "episodic")
            self.semantic_store = SQLiteMemoryStore(agent_id, "semantic")
        else:
            raise ValueError(f"Unknown store type: {store_type}")

        logger.debug(
            f"Initialized AgentMemory for agent {agent_id} using {store_type} storage"
        )

    # State memory methods (for agent state persistence)

    def save_state(self, key: str, value: Any) -> None:
        """Save a state variable"""
        self.state_store.save(key, value)

    def load_state(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Load a state variable"""
        return self.state_store.load(key, default)

    def delete_state(self, key: str) -> bool:
        """Delete a state variable"""
        return self.state_store.delete(key)

    def list_state_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all state variable keys"""
        return self.state_store.list_keys(prefix)

    def clear_state(self) -> None:
        """Clear all state variables"""
        self.state_store.clear()

    # Episodic memory methods (for storing event sequences)

    def add_episode(
        self,
        content: Any,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add an episodic memory (event or experience).

        Returns the ID of the created memory.
        """
        # Generate a timestamp-based ID
        timestamp = datetime.now()
        memory_id = f"episode_{timestamp.isoformat().replace(':', '_')}"

        # Create memory entry
        entry = MemoryEntry(content, tags, timestamp, metadata)

        # Save to store
        self.episodic_store.save(memory_id, entry.to_dict())

        return memory_id

    def get_episode(self, episode_id: str) -> Optional[MemoryEntry]:
        """Get an episodic memory by ID"""
        data = self.episodic_store.load(episode_id)
        if data is None:
            return None

        return MemoryEntry.from_dict(data)

    def list_episodes(
        self,
        tag: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Tuple[str, MemoryEntry]]:
        """
        List episodic memories with optional filtering.

        Returns a list of (episode_id, entry) tuples.
        """
        # Get all episode IDs
        episode_ids = self.episodic_store.list_keys()

        result = []
        for episode_id in episode_ids:
            entry_data = self.episodic_store.load(episode_id)
            if entry_data is None:
                continue

            entry = MemoryEntry.from_dict(entry_data)

            # Apply filters
            if tag and tag not in entry.tags:
                continue

            if start_time and entry.timestamp < start_time:
                continue

            if end_time and entry.timestamp > end_time:
                continue

            result.append((episode_id, entry))

            # Apply limit
            if len(result) >= limit:
                break

        # Sort by timestamp (latest first)
        result.sort(key=lambda x: x[1].timestamp, reverse=True)

        return result

    def delete_episode(self, episode_id: str) -> bool:
        """Delete an episodic memory"""
        return self.episodic_store.delete(episode_id)

    def clear_episodes(self) -> None:
        """Clear all episodic memories"""
        self.episodic_store.clear()

    # Semantic memory methods (for storing knowledge and concepts)

    def save_semantic(
        self, key: str, content: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save a semantic memory (knowledge or concept)"""
        entry = {
            "content": content,
            "metadata": metadata or {},
            "updated_at": datetime.now().isoformat(),
        }
        self.semantic_store.save(key, entry)

    def get_semantic(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a semantic memory by key"""
        return self.semantic_store.load(key)

    def list_semantic_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all semantic memory keys"""
        return self.semantic_store.list_keys(prefix)

    def delete_semantic(self, key: str) -> bool:
        """Delete a semantic memory"""
        return self.semantic_store.delete(key)

    def clear_semantic(self) -> None:
        """Clear all semantic memories"""
        self.semantic_store.clear()

    # Utility methods

    def clear_all(self) -> None:
        """Clear all memories (state, episodic, and semantic)"""
        self.clear_state()
        self.clear_episodes()
        self.clear_semantic()

    def export_all(self) -> Dict[str, Any]:
        """Export all memories as a dictionary"""
        export = {
            "agent_id": self.agent_id,
            "export_time": datetime.now().isoformat(),
            "state": {},
            "episodic": {},
            "semantic": {},
        }

        # Export state
        for key in self.list_state_keys():
            export["state"][key] = self.load_state(key)

        # Export episodic
        for episode_id, entry in self.list_episodes(limit=1000000):
            export["episodic"][episode_id] = entry.to_dict()

        # Export semantic
        for key in self.list_semantic_keys():
            export["semantic"][key] = self.get_semantic(key)

        return export

    def import_from(self, export_data: Dict[str, Any]) -> None:
        """Import memories from an export dictionary"""
        if export_data.get("agent_id") != self.agent_id:
            logger.warning(
                f"Importing from different agent ID: {export_data.get('agent_id')}"
            )

        # Import state
        for key, value in export_data.get("state", {}).items():
            self.save_state(key, value)

        # Import episodic
        for episode_id, entry_data in export_data.get("episodic", {}).items():
            self.episodic_store.save(episode_id, entry_data)

        # Import semantic
        for key, value in export_data.get("semantic", {}).items():
            self.semantic_store.save(key, value)

        logger.info(f"Imported memory for agent {self.agent_id}")
