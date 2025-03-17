"""
Troubleshooter module for DockerForge.

This module provides functionality to troubleshoot Docker issues
using AI-powered analysis.
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.docker.connection_manager import get_docker_client, DockerConnectionError
from src.platforms.platform_adapter import get_platform_adapter
from src.core.ai_provider import get_ai_provider, AIProviderError

logger = get_logger("troubleshooter")


class TroubleshooterError(Exception):
    """Exception raised for troubleshooter errors."""
    pass


class DockerTroubleshooter:
    """Docker troubleshooter using AI-powered analysis."""

    def __init__(self, ai_provider_name: Optional[str] = None):
        """
        Initialize the Docker troubleshooter.
        
        Args:
            ai_provider_name: AI provider name (default: from config)
        """
        self.platform_adapter = get_platform_adapter()
        
        try:
            self.docker_client = get_docker_client()
        except DockerConnectionError as e:
            logger.warning(f"Docker connection error: {str(e)}")
            self.docker_client = None
        
        try:
            self.ai_provider = get_ai_provider(ai_provider_name)
        except AIProviderError as e:
            logger.warning(f"AI provider error: {str(e)}")
            self.ai_provider = None

    def check_docker_status(self) -> Dict[str, Any]:
        """
        Check Docker status.
        
        Returns:
            Dict[str, Any]: Docker status information
        """
        status = {
            "connected": False,
            "version": None,
            "info": None,
            "containers": {
                "total": 0,
                "running": 0,
                "paused": 0,
                "stopped": 0,
            },
            "images": 0,
        }
        
        if not self.docker_client:
            try:
                self.docker_client = get_docker_client()
            except DockerConnectionError as e:
                logger.error(f"Docker connection error: {str(e)}")
                status["error"] = str(e)
                return status
        
        try:
            # Get Docker version
            version = self.docker_client.version()
            status["version"] = version
            
            # Get Docker info
            info = self.docker_client.info()
            status["info"] = info
            
            # Get container counts
            status["containers"]["total"] = info.get("Containers", 0)
            status["containers"]["running"] = info.get("ContainersRunning", 0)
            status["containers"]["paused"] = info.get("ContainersPaused", 0)
            status["containers"]["stopped"] = info.get("ContainersStopped", 0)
            
            # Get image count
            status["images"] = info.get("Images", 0)
            
            status["connected"] = True
        except Exception as e:
            logger.error(f"Error checking Docker status: {str(e)}")
            status["error"] = str(e)
        
        return status

    def collect_container_logs(self, container_id: str, tail: int = 1000) -> Dict[str, Any]:
        """
        Collect logs from a container.
        
        Args:
            container_id: Container ID or name
            tail: Number of lines to collect from the end of the logs
            
        Returns:
            Dict[str, Any]: Container logs and information
            
        Raises:
            TroubleshooterError: If container is not found or logs cannot be collected
        """
        if not self.docker_client:
            try:
                self.docker_client = get_docker_client()
            except DockerConnectionError as e:
                raise TroubleshooterError(f"Docker connection error: {str(e)}")
        
        try:
            # Get container
            container = self.docker_client.containers.get(container_id)
            
            # Get container details
            details = container.attrs
            
            # Get container logs
            logs = container.logs(tail=tail, timestamps=True).decode("utf-8")
            
            return {
                "container_id": container.id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "status": container.status,
                "created": details["Created"],
                "logs": logs,
                "details": details,
            }
        except Exception as e:
            logger.error(f"Error collecting container logs: {str(e)}")
            raise TroubleshooterError(f"Error collecting container logs: {str(e)}")

    def collect_system_info(self) -> Dict[str, Any]:
        """
        Collect system information.
        
        Returns:
            Dict[str, Any]: System information
        """
        info = {
            "platform": self.platform_adapter.platform_info.to_dict(),
        }
        
        # Get Docker info
        docker_status = self.check_docker_status()
        if docker_status["connected"]:
            info["docker"] = docker_status
        
        # Get system resources
        try:
            import psutil
            
            info["resources"] = {
                "cpu": {
                    "count": psutil.cpu_count(),
                    "usage": psutil.cpu_percent(interval=1),
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "percent": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total": psutil.disk_usage("/").total,
                    "free": psutil.disk_usage("/").free,
                    "used": psutil.disk_usage("/").used,
                    "percent": psutil.disk_usage("/").percent,
                },
            }
        except ImportError:
            logger.warning("psutil not available, skipping system resource collection")
        
        return info

    def analyze_container(self, container_id: str, confirm_cost: bool = True) -> Dict[str, Any]:
        """
        Analyze a container using AI.
        
        Args:
            container_id: Container ID or name
            confirm_cost: Whether to confirm cost before analysis
            
        Returns:
            Dict[str, Any]: Analysis result
            
        Raises:
            TroubleshooterError: If container is not found or analysis fails
        """
        if not self.ai_provider:
            try:
                self.ai_provider = get_ai_provider()
            except AIProviderError as e:
                raise TroubleshooterError(f"AI provider error: {str(e)}")
        
        try:
            # Collect container logs and information
            container_info = self.collect_container_logs(container_id)
            
            # Collect system information
            system_info = self.collect_system_info()
            
            # Prepare context for AI analysis
            context = {
                "container": container_info,
                "system": system_info,
            }
            
            # Prepare query
            query = f"Analyze the logs and information for container {container_id} and identify any issues or potential problems."
            
            # Estimate cost
            if confirm_cost:
                # Convert context to string for cost estimation
                context_str = json.dumps(context, indent=2)
                
                # Estimate cost
                cost_info = self.ai_provider.estimate_cost(context_str + "\n\n" + query)
                
                # Log cost information
                logger.info(
                    f"Estimated cost for container analysis: "
                    f"${cost_info['estimated_cost_usd']:.4f} "
                    f"({cost_info['input_tokens']} input tokens, "
                    f"{cost_info['output_tokens']} output tokens)"
                )
                
                # Confirm cost
                if not self.ai_provider.confirm_cost(cost_info):
                    raise TroubleshooterError(
                        f"Analysis cost exceeds budget limits: "
                        f"${cost_info['estimated_cost_usd']:.4f}"
                    )
            
            # Analyze with AI
            analysis = self.ai_provider.analyze(context, query)
            
            # Record usage if available
            try:
                if hasattr(self.ai_provider, 'usage_tracker') and self.ai_provider.usage_tracker:
                    # Extract token counts from response if available
                    input_tokens = cost_info['input_tokens'] if 'input_tokens' in locals() else 0
                    output_tokens = analysis.get('output_tokens', 0)
                    if 'raw_response' in analysis and 'usage' in analysis['raw_response']:
                        input_tokens = analysis['raw_response']['usage'].get('prompt_tokens', input_tokens)
                        output_tokens = analysis['raw_response']['usage'].get('completion_tokens', output_tokens)
                    
                    # Calculate cost
                    cost = 0.0
                    if 'estimated_cost_usd' in locals() and 'cost_info' in locals():
                        cost = cost_info['estimated_cost_usd']
                    
                    # Record usage
                    self.ai_provider.usage_tracker.record_usage(
                        provider=analysis['provider'],
                        model=analysis['model'],
                        operation='analyze_container',
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost_usd=cost,
                    )
            except Exception as e:
                logger.debug(f"Error recording usage: {str(e)}")
            
            return {
                "container_id": container_id,
                "container_name": container_info["name"],
                "container_status": container_info["status"],
                "analysis": analysis["analysis"],
                "provider": analysis["provider"],
                "model": analysis["model"],
            }
        except Exception as e:
            logger.error(f"Error analyzing container: {str(e)}")
            raise TroubleshooterError(f"Error analyzing container: {str(e)}")

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fix for an issue using AI.
        
        Args:
            issue: Issue information
            
        Returns:
            Dict[str, Any]: Fix information
            
        Raises:
            TroubleshooterError: If fix generation fails
        """
        if not self.ai_provider:
            try:
                self.ai_provider = get_ai_provider()
            except AIProviderError as e:
                raise TroubleshooterError(f"AI provider error: {str(e)}")
        
        try:
            # Generate fix with AI
            fix = self.ai_provider.generate_fix(issue)
            
            return {
                "issue": issue,
                "fix": fix["fix"],
                "provider": fix["provider"],
                "model": fix["model"],
            }
        except Exception as e:
            logger.error(f"Error generating fix: {str(e)}")
            raise TroubleshooterError(f"Error generating fix: {str(e)}")

    def analyze_logs(self, logs: str) -> Dict[str, Any]:
        """
        Analyze logs using AI.
        
        Args:
            logs: Logs to analyze
            
        Returns:
            Dict[str, Any]: Analysis result
            
        Raises:
            TroubleshooterError: If analysis fails
        """
        if not self.ai_provider:
            try:
                self.ai_provider = get_ai_provider()
            except AIProviderError as e:
                raise TroubleshooterError(f"AI provider error: {str(e)}")
        
        try:
            # Collect system information
            system_info = self.collect_system_info()
            
            # Prepare context for AI analysis
            context = {
                "logs": logs,
                "system": system_info,
            }
            
            # Analyze with AI
            query = "Analyze these logs and identify any issues or potential problems."
            analysis = self.ai_provider.analyze(context, query)
            
            return {
                "analysis": analysis["analysis"],
                "provider": analysis["provider"],
                "model": analysis["model"],
            }
        except Exception as e:
            logger.error(f"Error analyzing logs: {str(e)}")
            raise TroubleshooterError(f"Error analyzing logs: {str(e)}")

    def analyze_docker_compose(self, compose_file: str) -> Dict[str, Any]:
        """
        Analyze a Docker Compose file using AI.
        
        Args:
            compose_file: Path to Docker Compose file or content
            
        Returns:
            Dict[str, Any]: Analysis result
            
        Raises:
            TroubleshooterError: If analysis fails
        """
        if not self.ai_provider:
            try:
                self.ai_provider = get_ai_provider()
            except AIProviderError as e:
                raise TroubleshooterError(f"AI provider error: {str(e)}")
        
        try:
            # Check if compose_file is a path or content
            if os.path.exists(compose_file):
                with open(compose_file, "r") as f:
                    content = f.read()
            else:
                content = compose_file
            
            # Collect system information
            system_info = self.collect_system_info()
            
            # Prepare context for AI analysis
            context = {
                "docker_compose": content,
                "system": system_info,
            }
            
            # Analyze with AI
            query = "Analyze this Docker Compose file and identify any issues, potential problems, or improvements."
            analysis = self.ai_provider.analyze(context, query)
            
            return {
                "analysis": analysis["analysis"],
                "provider": analysis["provider"],
                "model": analysis["model"],
            }
        except Exception as e:
            logger.error(f"Error analyzing Docker Compose file: {str(e)}")
            raise TroubleshooterError(f"Error analyzing Docker Compose file: {str(e)}")

    def analyze_dockerfile(self, dockerfile: str) -> Dict[str, Any]:
        """
        Analyze a Dockerfile using AI.
        
        Args:
            dockerfile: Path to Dockerfile or content
            
        Returns:
            Dict[str, Any]: Analysis result
            
        Raises:
            TroubleshooterError: If analysis fails
        """
        if not self.ai_provider:
            try:
                self.ai_provider = get_ai_provider()
            except AIProviderError as e:
                raise TroubleshooterError(f"AI provider error: {str(e)}")
        
        try:
            # Check if dockerfile is a path or content
            if os.path.exists(dockerfile):
                with open(dockerfile, "r") as f:
                    content = f.read()
            else:
                content = dockerfile
            
            # Collect system information
            system_info = self.collect_system_info()
            
            # Prepare context for AI analysis
            context = {
                "dockerfile": content,
                "system": system_info,
            }
            
            # Analyze with AI
            query = "Analyze this Dockerfile and identify any issues, potential problems, or improvements."
            analysis = self.ai_provider.analyze(context, query)
            
            return {
                "analysis": analysis["analysis"],
                "provider": analysis["provider"],
                "model": analysis["model"],
            }
        except Exception as e:
            logger.error(f"Error analyzing Dockerfile: {str(e)}")
            raise TroubleshooterError(f"Error analyzing Dockerfile: {str(e)}")

    def troubleshoot_connection(self) -> Dict[str, Any]:
        """
        Troubleshoot Docker connection issues.
        
        Returns:
            Dict[str, Any]: Troubleshooting result
        """
        result = {
            "connected": False,
            "issues": [],
            "fixes": [],
        }
        
        # Check if Docker is running
        docker_status = self.check_docker_status()
        if docker_status["connected"]:
            result["connected"] = True
            return result
        
        # Collect system information
        system_info = self.collect_system_info()
        platform_info = system_info["platform"]
        
        # Check common issues based on platform
        if platform_info["platform_type"] == "linux":
            # Check if Docker socket exists
            socket_path = platform_info["docker_socket_path"]
            if not os.path.exists(socket_path):
                result["issues"].append(f"Docker socket not found at {socket_path}")
                result["fixes"].append("Make sure Docker is installed and running")
                result["fixes"].append("sudo systemctl start docker")
            
            # Check if user has permission to access Docker socket
            if os.path.exists(socket_path):
                try:
                    import stat
                    socket_stat = os.stat(socket_path)
                    socket_mode = socket_stat.st_mode
                    socket_group = socket_stat.st_gid
                    
                    # Check if socket is a socket
                    if not stat.S_ISSOCK(socket_mode):
                        result["issues"].append(f"{socket_path} is not a socket")
                        result["fixes"].append("Check Docker installation")
                    
                    # Check if socket has correct permissions
                    import grp
                    try:
                        docker_group = grp.getgrgid(socket_group).gr_name
                        
                        # Check if current user is in docker group
                        import pwd
                        current_user = pwd.getpwuid(os.getuid()).pw_name
                        user_groups = [g.gr_name for g in grp.getgrall() if current_user in g.gr_mem]
                        
                        if docker_group not in user_groups and os.getuid() != 0:
                            result["issues"].append(f"User {current_user} is not in the {docker_group} group")
                            result["fixes"].append(f"Add user to the {docker_group} group: sudo usermod -aG {docker_group} {current_user}")
                            result["fixes"].append("Log out and log back in for the changes to take effect")
                    except KeyError:
                        pass
                except (ImportError, OSError):
                    pass
        
        elif platform_info["platform_type"] == "windows":
            # Check if Docker Desktop is installed
            if not os.path.exists("C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"):
                result["issues"].append("Docker Desktop not found")
                result["fixes"].append("Install Docker Desktop for Windows")
            
            # Check if Docker service is running
            try:
                import subprocess
                output = subprocess.check_output(["sc", "query", "com.docker.service"], universal_newlines=True)
                if "RUNNING" not in output:
                    result["issues"].append("Docker service is not running")
                    result["fixes"].append("Start Docker Desktop")
            except (subprocess.SubprocessError, FileNotFoundError):
                result["issues"].append("Could not check Docker service status")
                result["fixes"].append("Make sure Docker Desktop is installed and running")
        
        elif platform_info["platform_type"] == "darwin":
            # Check if Docker Desktop is installed
            if not os.path.exists("/Applications/Docker.app"):
                result["issues"].append("Docker Desktop not found")
                result["fixes"].append("Install Docker Desktop for Mac")
            
            # Check if Docker Desktop is running
            try:
                import subprocess
                output = subprocess.check_output(["pgrep", "Docker"], universal_newlines=True)
                if not output.strip():
                    result["issues"].append("Docker Desktop is not running")
                    result["fixes"].append("Start Docker Desktop")
            except (subprocess.SubprocessError, FileNotFoundError):
                result["issues"].append("Could not check Docker Desktop status")
                result["fixes"].append("Make sure Docker Desktop is installed and running")
        
        # If no specific issues found, add generic advice
        if not result["issues"]:
            result["issues"].append("Could not connect to Docker daemon")
            result["fixes"].append("Make sure Docker is installed and running")
            result["fixes"].append("Check Docker configuration")
        
        return result


# Singleton instance
_troubleshooter = None


def get_troubleshooter(ai_provider_name: Optional[str] = None) -> DockerTroubleshooter:
    """
    Get the Docker troubleshooter (singleton).
    
    Args:
        ai_provider_name: AI provider name (default: from config)
        
    Returns:
        DockerTroubleshooter: Docker troubleshooter
    """
    global _troubleshooter
    if _troubleshooter is None:
        _troubleshooter = DockerTroubleshooter(ai_provider_name)
    
    return _troubleshooter
