"""
Terminal service for the DockerForge Web UI.

This module provides terminal services for interacting with Docker containers.
"""
from typing import Dict, Any, Optional, List, Tuple
import logging
import asyncio
import uuid
import time
import docker
from docker.errors import DockerException
from fastapi import WebSocket

# Configure logging
logger = logging.getLogger(__name__)

# Docker client
docker_client = docker.from_env()

# Store active terminal sessions
class TerminalManager:
    def __init__(self):
        # Dictionary mapping session IDs to terminal sessions
        self.active_sessions: Dict[str, "TerminalSession"] = {}
        
    def create_session(self, container_id: str, user_id: str, cols: int = 80, rows: int = 24) -> str:
        """
        Create a new terminal session for a container.
        
        Args:
            container_id: Container ID
            user_id: User ID
            cols: Number of columns
            rows: Number of rows
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session = TerminalSession(session_id, container_id, user_id, cols, rows)
        self.active_sessions[session_id] = session
        logger.info(f"Created terminal session {session_id} for container {container_id} by user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional["TerminalSession"]:
        """
        Get a terminal session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Terminal session or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """
        Close a terminal session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session was closed, False if not found
        """
        session = self.active_sessions.get(session_id)
        if session:
            session.close()
            del self.active_sessions[session_id]
            logger.info(f"Closed terminal session {session_id}")
            return True
        return False
    
    def close_user_sessions(self, user_id: str) -> int:
        """
        Close all terminal sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions closed
        """
        count = 0
        sessions_to_close = [
            session_id for session_id, session in self.active_sessions.items()
            if session.user_id == user_id
        ]
        
        for session_id in sessions_to_close:
            if self.close_session(session_id):
                count += 1
                
        return count
    
    def close_container_sessions(self, container_id: str) -> int:
        """
        Close all terminal sessions for a container.
        
        Args:
            container_id: Container ID
            
        Returns:
            Number of sessions closed
        """
        count = 0
        sessions_to_close = [
            session_id for session_id, session in self.active_sessions.items()
            if session.container_id == container_id
        ]
        
        for session_id in sessions_to_close:
            if self.close_session(session_id):
                count += 1
                
        return count
    
    def get_sessions_for_user(self, user_id: str) -> List["TerminalSession"]:
        """
        Get all terminal sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of terminal sessions
        """
        return [
            session for session in self.active_sessions.values()
            if session.user_id == user_id
        ]
    
    def get_sessions_for_container(self, container_id: str) -> List["TerminalSession"]:
        """
        Get all terminal sessions for a container.
        
        Args:
            container_id: Container ID
            
        Returns:
            List of terminal sessions
        """
        return [
            session for session in self.active_sessions.values()
            if session.container_id == container_id
        ]


class TerminalSession:
    def __init__(self, session_id: str, container_id: str, user_id: str, cols: int = 80, rows: int = 24):
        self.session_id = session_id
        self.container_id = container_id
        self.user_id = user_id
        self.cols = cols
        self.rows = rows
        self.created_at = time.time()
        self.last_activity = time.time()
        self.exec_id = None
        self.socket = None
        self.command_history: List[str] = []
        self.is_active = True
        
    async def connect(self, websocket: WebSocket) -> bool:
        """
        Connect a WebSocket to this terminal session.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.socket = websocket
            
            # Create exec instance in container
            container = docker_client.containers.get(self.container_id)
            
            # Check if container is running
            if container.status != "running":
                await websocket.send_json({
                    "type": "error",
                    "error": f"Container {self.container_id} is not running",
                    "timestamp": time.time()
                })
                return False
            
            # Create exec instance
            exec_instance = docker_client.api.exec_create(
                container.id,
                cmd=["/bin/sh"],
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True,
                environment={"TERM": "xterm-256color"}
            )
            
            self.exec_id = exec_instance["Id"]
            
            # Start exec instance
            exec_socket = docker_client.api.exec_start(
                self.exec_id,
                detach=False,
                tty=True,
                socket=True
            )
            
            # Start socket communication tasks
            asyncio.create_task(self._handle_container_output(exec_socket))
            
            logger.info(f"Connected terminal session {self.session_id} to container {self.container_id}")
            return True
            
        except DockerException as e:
            logger.error(f"Docker error connecting terminal session {self.session_id}: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "error": f"Docker error: {str(e)}",
                "timestamp": time.time()
            })
            return False
        except Exception as e:
            logger.error(f"Error connecting terminal session {self.session_id}: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "error": f"Error: {str(e)}",
                "timestamp": time.time()
            })
            return False
    
    async def send_input(self, data: str) -> bool:
        """
        Send input to the terminal.
        
        Args:
            data: Input data
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.exec_id:
                logger.error(f"Terminal session {self.session_id} not connected")
                return False
            
            # Send input to container
            docker_client.api.exec_resize(self.exec_id, height=self.rows, width=self.cols)
            
            # TODO: Implement sending input to container
            # This requires lower-level access to the Docker API socket
            
            self.last_activity = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Error sending input to terminal session {self.session_id}: {str(e)}")
            return False
    
    async def resize(self, cols: int, rows: int) -> bool:
        """
        Resize the terminal.
        
        Args:
            cols: Number of columns
            rows: Number of rows
            
        Returns:
            True if resized successfully, False otherwise
        """
        try:
            if not self.exec_id:
                logger.error(f"Terminal session {self.session_id} not connected")
                return False
            
            self.cols = cols
            self.rows = rows
            
            # Resize terminal
            docker_client.api.exec_resize(self.exec_id, height=rows, width=cols)
            
            self.last_activity = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Error resizing terminal session {self.session_id}: {str(e)}")
            return False
    
    def close(self) -> None:
        """
        Close the terminal session.
        """
        self.is_active = False
        self.exec_id = None
        self.socket = None
    
    async def _handle_container_output(self, socket) -> None:
        """
        Handle output from the container.
        
        Args:
            socket: Docker exec socket
        """
        try:
            while self.is_active and self.socket:
                # Read from Docker socket
                chunk = socket.read(4096)
                if not chunk:
                    break
                
                # Send to WebSocket
                await self.socket.send_bytes(chunk)
                
        except Exception as e:
            logger.error(f"Error handling container output for session {self.session_id}: {str(e)}")
            if self.socket:
                try:
                    await self.socket.send_json({
                        "type": "error",
                        "error": f"Terminal error: {str(e)}",
                        "timestamp": time.time()
                    })
                except:
                    pass
        finally:
            # Close the session
            self.close()


# Create terminal manager instance
terminal_manager = TerminalManager()


def get_terminal_manager() -> TerminalManager:
    """
    Get the terminal manager instance.
    
    Returns:
        Terminal manager
    """
    return terminal_manager
