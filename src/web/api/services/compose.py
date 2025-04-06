"""
Compose services for the DockerForge Web UI.

This module provides the service functions for Docker Compose management.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio
import yaml
import os
import tempfile
from sqlalchemy.orm import Session

from src.web.api.schemas.compose import ComposeFile, ComposeService
from src.web.api.services import docker

logger = logging.getLogger(__name__)


async def get_compose_files(
    name: Optional[str] = None,
    db: Session = None
) -> List[ComposeFile]:
    """
    Get all compose files.
    
    Args:
        name: Filter by compose file name
        db: Database session
        
    Returns:
        List[ComposeFile]: List of compose files
    """
    try:
        # In a real implementation, this would call the Docker API and read from the database
        # For now, we'll return mock data
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Mock compose files
        compose_files = [
            {
                "id": "compose1",
                "name": "Web Application",
                "path": "/home/user/projects/web-app/docker-compose.yml",
                "description": "Web application stack with Nginx, Node.js, and MongoDB",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "content": """
version: '3'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
    depends_on:
      - app
  app:
    image: node:14
    volumes:
      - ./app:/app
    working_dir: /app
    command: npm start
    environment:
      - NODE_ENV=production
      - MONGO_URL=mongodb://mongo:27017/app
    depends_on:
      - mongo
  mongo:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db
volumes:
  mongo-data:
""",
                "services_count": 3,
                "status": "running",
                "services": [
                    {
                        "name": "nginx",
                        "image": "nginx:latest",
                        "status": "running",
                        "ports": ["80:80"],
                        "volumes": ["./nginx/conf:/etc/nginx/conf.d"],
                        "networks": ["default"],
                        "depends_on": ["app"],
                        "container_id": "container1",
                        "container_name": "web-app_nginx_1"
                    },
                    {
                        "name": "app",
                        "image": "node:14",
                        "status": "running",
                        "volumes": ["./app:/app"],
                        "networks": ["default"],
                        "depends_on": ["mongo"],
                        "environment": {
                            "NODE_ENV": "production",
                            "MONGO_URL": "mongodb://mongo:27017/app"
                        },
                        "command": "npm start",
                        "container_id": "container2",
                        "container_name": "web-app_app_1"
                    },
                    {
                        "name": "mongo",
                        "image": "mongo:latest",
                        "status": "running",
                        "volumes": ["mongo-data:/data/db"],
                        "networks": ["default"],
                        "container_id": "container3",
                        "container_name": "web-app_mongo_1"
                    }
                ]
            },
            {
                "id": "compose2",
                "name": "WordPress",
                "path": "/home/user/projects/wordpress/docker-compose.yml",
                "description": "WordPress with MySQL",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "content": """
version: '3'
services:
  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      - WORDPRESS_DB_HOST=mysql
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=wordpress
      - WORDPRESS_DB_NAME=wordpress
    depends_on:
      - mysql
  mysql:
    image: mysql:5.7
    environment:
      - MYSQL_ROOT_PASSWORD=somewordpress
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=wordpress
    volumes:
      - mysql-data:/var/lib/mysql
volumes:
  mysql-data:
""",
                "services_count": 2,
                "status": "stopped",
                "services": [
                    {
                        "name": "wordpress",
                        "image": "wordpress:latest",
                        "status": "stopped",
                        "ports": ["8080:80"],
                        "networks": ["default"],
                        "depends_on": ["mysql"],
                        "environment": {
                            "WORDPRESS_DB_HOST": "mysql",
                            "WORDPRESS_DB_USER": "wordpress",
                            "WORDPRESS_DB_PASSWORD": "wordpress",
                            "WORDPRESS_DB_NAME": "wordpress"
                        },
                        "container_id": None,
                        "container_name": "wordpress_wordpress_1"
                    },
                    {
                        "name": "mysql",
                        "image": "mysql:5.7",
                        "status": "stopped",
                        "volumes": ["mysql-data:/var/lib/mysql"],
                        "networks": ["default"],
                        "environment": {
                            "MYSQL_ROOT_PASSWORD": "somewordpress",
                            "MYSQL_DATABASE": "wordpress",
                            "MYSQL_USER": "wordpress",
                            "MYSQL_PASSWORD": "wordpress"
                        },
                        "container_id": None,
                        "container_name": "wordpress_mysql_1"
                    }
                ]
            },
            {
                "id": "compose3",
                "name": "Monitoring Stack",
                "path": "/home/user/projects/monitoring/docker-compose.yml",
                "description": "Prometheus, Grafana, and Node Exporter",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "content": """
version: '3'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command: --config.file=/etc/prometheus/prometheus.yml
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
volumes:
  prometheus-data:
  grafana-data:
""",
                "services_count": 3,
                "status": "partial",
                "services": [
                    {
                        "name": "prometheus",
                        "image": "prom/prometheus:latest",
                        "status": "running",
                        "ports": ["9090:9090"],
                        "volumes": [
                            "./prometheus:/etc/prometheus",
                            "prometheus-data:/prometheus"
                        ],
                        "networks": ["default"],
                        "command": "--config.file=/etc/prometheus/prometheus.yml",
                        "container_id": "container4",
                        "container_name": "monitoring_prometheus_1"
                    },
                    {
                        "name": "grafana",
                        "image": "grafana/grafana:latest",
                        "status": "running",
                        "ports": ["3000:3000"],
                        "volumes": ["grafana-data:/var/lib/grafana"],
                        "networks": ["default"],
                        "depends_on": ["prometheus"],
                        "container_id": "container5",
                        "container_name": "monitoring_grafana_1"
                    },
                    {
                        "name": "node-exporter",
                        "image": "prom/node-exporter:latest",
                        "status": "stopped",
                        "ports": ["9100:9100"],
                        "volumes": [
                            "/proc:/host/proc:ro",
                            "/sys:/host/sys:ro",
                            "/:/rootfs:ro"
                        ],
                        "networks": ["default"],
                        "command": "--path.procfs=/host/proc --path.sysfs=/host/sys --path.rootfs=/rootfs",
                        "container_id": None,
                        "container_name": "monitoring_node-exporter_1"
                    }
                ]
            }
        ]
        
        # Apply filters
        filtered_files = compose_files
        
        if name:
            filtered_files = [f for f in filtered_files if name.lower() in f["name"].lower()]
        
        # Convert to ComposeFile schema
        return [ComposeFile(**file) for file in filtered_files]
    except Exception as e:
        logger.error(f"Failed to get compose files: {e}")
        raise


async def get_compose_file(file_id: str, db: Session = None) -> Optional[ComposeFile]:
    """
    Get a compose file by ID.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        Optional[ComposeFile]: Compose file if found, None otherwise
    """
    try:
        # Get all compose files
        compose_files = await get_compose_files(db=db)
        
        # Find the compose file with the given ID
        for compose_file in compose_files:
            if compose_file.id == file_id:
                return compose_file
        
        return None
    except Exception as e:
        logger.error(f"Failed to get compose file: {e}")
        raise


async def create_compose_file(
    name: str,
    path: str,
    content: str,
    description: Optional[str] = None,
    db: Session = None
) -> ComposeFile:
    """
    Create a new compose file.
    
    Args:
        name: Compose file name
        path: Compose file path
        content: Compose file content
        description: Compose file description
        db: Database session
        
    Returns:
        ComposeFile: Created compose file
    """
    try:
        # In a real implementation, this would save the file to disk and database
        # For now, we'll simulate the creation
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Validate YAML content
        try:
            yaml_content = yaml.safe_load(content)
            if not yaml_content or not isinstance(yaml_content, dict) or 'services' not in yaml_content:
                raise ValueError("Invalid Docker Compose file format")
            
            services_count = len(yaml_content.get('services', {}))
        except Exception as e:
            raise ValueError(f"Invalid YAML content: {str(e)}")
        
        # Create compose file
        compose_file = {
            "id": f"compose{datetime.now().timestamp()}",
            "name": name,
            "path": path,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "content": content,
            "services_count": services_count,
            "status": "created",
            "services": []
        }
        
        # Parse services from YAML
        services = []
        for service_name, service_config in yaml_content.get('services', {}).items():
            service = {
                "name": service_name,
                "image": service_config.get('image', 'unknown'),
                "status": "created",
                "ports": service_config.get('ports', []),
                "volumes": service_config.get('volumes', []),
                "networks": service_config.get('networks', ['default']),
                "depends_on": service_config.get('depends_on', []),
                "environment": service_config.get('environment', {}),
                "command": service_config.get('command', None),
                "container_id": None,
                "container_name": f"{name.lower().replace(' ', '_')}_{service_name}_1"
            }
            services.append(service)
        
        compose_file["services"] = services
        
        return ComposeFile(**compose_file)
    except Exception as e:
        logger.error(f"Failed to create compose file: {e}")
        raise


async def update_compose_file(
    file_id: str,
    name: Optional[str] = None,
    path: Optional[str] = None,
    content: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = None
) -> Optional[ComposeFile]:
    """
    Update a compose file.
    
    Args:
        file_id: Compose file ID
        name: Compose file name
        path: Compose file path
        content: Compose file content
        description: Compose file description
        db: Database session
        
    Returns:
        Optional[ComposeFile]: Updated compose file if found, None otherwise
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            return None
        
        # In a real implementation, this would update the file on disk and in the database
        # For now, we'll simulate the update
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Update compose file
        updated_file = compose_file.dict()
        
        if name is not None:
            updated_file["name"] = name
        
        if path is not None:
            updated_file["path"] = path
        
        if description is not None:
            updated_file["description"] = description
        
        if content is not None:
            # Validate YAML content
            try:
                yaml_content = yaml.safe_load(content)
                if not yaml_content or not isinstance(yaml_content, dict) or 'services' not in yaml_content:
                    raise ValueError("Invalid Docker Compose file format")
                
                services_count = len(yaml_content.get('services', {}))
                updated_file["services_count"] = services_count
                updated_file["content"] = content
                
                # Parse services from YAML
                services = []
                for service_name, service_config in yaml_content.get('services', {}).items():
                    # Check if service already exists
                    existing_service = next((s for s in updated_file["services"] if s["name"] == service_name), None)
                    
                    service = {
                        "name": service_name,
                        "image": service_config.get('image', 'unknown'),
                        "status": existing_service["status"] if existing_service else "created",
                        "ports": service_config.get('ports', []),
                        "volumes": service_config.get('volumes', []),
                        "networks": service_config.get('networks', ['default']),
                        "depends_on": service_config.get('depends_on', []),
                        "environment": service_config.get('environment', {}),
                        "command": service_config.get('command', None),
                        "container_id": existing_service["container_id"] if existing_service else None,
                        "container_name": existing_service["container_name"] if existing_service else f"{updated_file['name'].lower().replace(' ', '_')}_{service_name}_1"
                    }
                    services.append(service)
                
                updated_file["services"] = services
            except Exception as e:
                raise ValueError(f"Invalid YAML content: {str(e)}")
        
        updated_file["updated_at"] = datetime.now().isoformat()
        
        return ComposeFile(**updated_file)
    except Exception as e:
        logger.error(f"Failed to update compose file: {e}")
        raise


async def delete_compose_file(file_id: str, db: Session = None) -> bool:
    """
    Delete a compose file.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            return False
        
        # In a real implementation, this would delete the file from disk and database
        # For now, we'll simulate the deletion
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Check if any services are running
        if compose_file.status == "running" or compose_file.status == "partial":
            # Stop the compose project first
            await compose_down(file_id=file_id, db=db)
        
        return True
    except Exception as e:
        logger.error(f"Failed to delete compose file: {e}")
        raise


async def get_compose_services(file_id: str, db: Session = None) -> List[ComposeService]:
    """
    Get services for a compose file.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        List[ComposeService]: List of compose services
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise ValueError(f"Compose file with ID {file_id} not found")
        
        # Return services
        return compose_file.services or []
    except Exception as e:
        logger.error(f"Failed to get compose services: {e}")
        raise


async def compose_up(file_id: str, db: Session = None) -> Dict[str, Any]:
    """
    Start a compose project.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise ValueError(f"Compose file with ID {file_id} not found")
        
        # In a real implementation, this would call docker-compose up
        # For now, we'll simulate the operation
        await asyncio.sleep(1.0)  # Simulate API call delay
        
        # Update service status
        for service in compose_file.services:
            service.status = "running"
            service.container_id = f"container{datetime.now().timestamp()}"
        
        # Update compose file status
        compose_file_dict = compose_file.dict()
        compose_file_dict["status"] = "running"
        compose_file_dict["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": f"Compose project {compose_file.name} started successfully",
            "services_started": len(compose_file.services)
        }
    except Exception as e:
        logger.error(f"Failed to start compose project: {e}")
        raise


async def compose_down(file_id: str, db: Session = None) -> Dict[str, Any]:
    """
    Stop a compose project.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise ValueError(f"Compose file with ID {file_id} not found")
        
        # In a real implementation, this would call docker-compose down
        # For now, we'll simulate the operation
        await asyncio.sleep(1.0)  # Simulate API call delay
        
        # Update service status
        for service in compose_file.services:
            service.status = "stopped"
            service.container_id = None
        
        # Update compose file status
        compose_file_dict = compose_file.dict()
        compose_file_dict["status"] = "stopped"
        compose_file_dict["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": f"Compose project {compose_file.name} stopped successfully",
            "services_stopped": len(compose_file.services)
        }
    except Exception as e:
        logger.error(f"Failed to stop compose project: {e}")
        raise


async def compose_restart(file_id: str, db: Session = None) -> Dict[str, Any]:
    """
    Restart a compose project.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise ValueError(f"Compose file with ID {file_id} not found")
        
        # In a real implementation, this would call docker-compose restart
        # For now, we'll simulate the operation
        await asyncio.sleep(1.0)  # Simulate API call delay
        
        # Update service status
        for service in compose_file.services:
            service.status = "running"
            if not service.container_id:
                service.container_id = f"container{datetime.now().timestamp()}"
        
        # Update compose file status
        compose_file_dict = compose_file.dict()
        compose_file_dict["status"] = "running"
        compose_file_dict["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": f"Compose project {compose_file.name} restarted successfully",
            "services_restarted": len(compose_file.services)
        }
    except Exception as e:
        logger.error(f"Failed to restart compose project: {e}")
        raise


async def compose_pull(file_id: str, db: Session = None) -> Dict[str, Any]:
    """
    Pull images for a compose project.
    
    Args:
        file_id: Compose file ID
        db: Database session
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise ValueError(f"Compose file with ID {file_id} not found")
        
        # In a real implementation, this would call docker-compose pull
        # For now, we'll simulate the operation
        await asyncio.sleep(2.0)  # Simulate API call delay
        
        return {
            "success": True,
            "message": f"Images for compose project {compose_file.name} pulled successfully",
            "images_pulled": len(compose_file.services)
        }
    except Exception as e:
        logger.error(f"Failed to pull compose images: {e}")
        raise


async def get_compose_logs(
    file_id: str,
    service: Optional[str] = None,
    tail: Optional[int] = 100,
    db: Session = None
) -> Dict[str, Any]:
    """
    Get logs for a compose project.
    
    Args:
        file_id: Compose file ID
        service: Service name
        tail: Number of lines to tail
        db: Database session
        
    Returns:
        Dict[str, Any]: Logs for the compose project
    """
    try:
        # Get the compose file
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise ValueError(f"Compose file with ID {file_id} not found")
        
        # In a real implementation, this would call docker-compose logs
        # For now, we'll return mock logs
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        logs = {}
        
        if service:
            # Get logs for a specific service
            service_obj = next((s for s in compose_file.services if s.name == service), None)
            if not service_obj:
                raise ValueError(f"Service {service} not found in compose file {compose_file.name}")
            
            logs[service] = [
                f"[{service}] {datetime.now().isoformat()} Log line {i+1}" for i in range(tail)
            ]
        else:
            # Get logs for all services
            for service_obj in compose_file.services:
                logs[service_obj.name] = [
                    f"[{service_obj.name}] {datetime.now().isoformat()} Log line {i+1}" for i in range(tail)
                ]
        
        return {
            "logs": logs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get compose logs: {e}")
        raise
