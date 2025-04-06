"""
Image service for the DockerForge Web UI.

This module provides the image management services for the DockerForge Web UI.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio
import tempfile
import os
from sqlalchemy.orm import Session

from src.web.api.schemas.images import Image, ImageCreate, ImageUpdate, ImageScan, ImageVulnerability, ImageScanResult, DockerfileValidation, DockerfileBuild
from src.web.api.services import docker
from src.web.api.models.image import Image as ImageModel, SecurityScan, Vulnerability
from src.core.troubleshooter import get_troubleshooter, TroubleshooterError

# Configure logging
logger = logging.getLogger(__name__)


async def get_images(
    name: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: Session = None,
) -> List[Image]:
    """
    Get all images with optional filtering.
    """
    try:
        # Get images from Docker API
        docker_images = docker.get_images()

        # Filter images
        filtered_images = docker_images
        if name:
            filtered_images = [img for img in filtered_images if any(name in tag.split(':')[0] for tag in img.get('tags', []) if tag)]
        if tag:
            filtered_images = [img for img in filtered_images if any(tag == tag.split(':')[1] for tag in img.get('tags', []) if tag and ':' in tag)]

        # Apply pagination
        paginated_images = filtered_images[skip:skip + limit]

        # Convert to Image objects
        return [Image(**image) for image in paginated_images]
    except Exception as e:
        logger.error(f"Failed to get images: {e}")
        raise


async def get_image(image_id: str, db: Session = None) -> Optional[Image]:
    """
    Get an image by ID.
    """
    try:
        # Get image from Docker API
        image_data = docker.get_image(image_id)
        if not image_data:
            return None

        # Convert to Image object
        return Image(**image_data)
    except Exception as e:
        logger.error(f"Failed to get image: {e}")
        raise


async def create_image(image: ImageCreate, db: Session = None) -> Image:
    """
    Create (pull) a new image.
    """
    try:
        # Prepare image name
        image_name = f"{image.name}:{image.tag}" if image.tag else image.name

        # Pull image using Docker API
        image_data = docker.pull_image(image_name)

        # Convert to Image object
        return Image(**image_data)
    except Exception as e:
        logger.error(f"Failed to create image: {e}")
        raise


async def delete_image(image_id: str, force: bool = False, db: Session = None) -> bool:
    """
    Delete an image by ID.
    """
    try:
        # Delete image using Docker API
        return docker.delete_image(image_id, force=force)
    except Exception as e:
        logger.error(f"Failed to delete image: {e}")
        raise


async def scan_image(image_id: str, scan_type: str = "vulnerability", db: Session = None) -> ImageScanResult:
    """
    Scan an image for vulnerabilities.

    Note: This is a placeholder implementation. In a real implementation, this would call a vulnerability scanner.
    """
    try:
        # Get image
        image = await get_image(image_id, db=db)
        if not image:
            raise ValueError(f"Image with ID {image_id} not found")

        # Check if image exists in database
        db_image = db.query(ImageModel).filter(ImageModel.docker_id == image_id).first()
        if not db_image:
            # Create image in database
            db_image = ImageModel(
                name=image.name,
                tag=image.tag,
                docker_id=image.docker_id,
                size=image.size,
                digest=image.digest,
                created_at_docker=image.created_at,
                author=image.author,
                architecture=image.architecture,
                os=image.os,
                labels=image.labels,
            )
            db.add(db_image)
            db.commit()
            db.refresh(db_image)

        # Create security scan
        scan = SecurityScan(
            image_id=db_image.id,
            scan_type=scan_type,
            status="running",
            started_at=datetime.now(),
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Placeholder: In a real implementation, this would call a vulnerability scanner
        # For now, we'll just create some mock vulnerabilities
        vulnerabilities = [
            Vulnerability(
                scan_id=scan.id,
                name="CVE-2023-1234",
                description="A critical vulnerability in the base image",
                severity="critical",
                package_name="openssl",
                package_version="1.1.1k",
                fixed_version="1.1.1l",
                reference_urls=["https://nvd.nist.gov/vuln/detail/CVE-2023-1234"],
                cve_id="CVE-2023-1234",
            ),
            Vulnerability(
                scan_id=scan.id,
                name="CVE-2023-5678",
                description="A high severity vulnerability in a package",
                severity="high",
                package_name="python",
                package_version="3.9.5",
                fixed_version="3.9.6",
                reference_urls=["https://nvd.nist.gov/vuln/detail/CVE-2023-5678"],
                cve_id="CVE-2023-5678",
            ),
            Vulnerability(
                scan_id=scan.id,
                name="CVE-2023-9012",
                description="A medium severity vulnerability in a package",
                severity="medium",
                package_name="nginx",
                package_version="1.21.0",
                fixed_version="1.21.1",
                reference_urls=["https://nvd.nist.gov/vuln/detail/CVE-2023-9012"],
                cve_id="CVE-2023-9012",
            ),
        ]

        for vulnerability in vulnerabilities:
            db.add(vulnerability)

        # Update scan status
        scan.status = "completed"
        scan.completed_at = datetime.now()
        scan.vulnerabilities_count = len(vulnerabilities)
        scan.critical_count = sum(1 for v in vulnerabilities if v.severity == "critical")
        scan.high_count = sum(1 for v in vulnerabilities if v.severity == "high")
        scan.medium_count = sum(1 for v in vulnerabilities if v.severity == "medium")
        scan.low_count = sum(1 for v in vulnerabilities if v.severity == "low")

        db.commit()
        db.refresh(scan)

        # Convert to ImageScan and ImageVulnerability objects
        scan_result = ImageScanResult(
            scan=ImageScan(
                id=scan.id,
                image_id=scan.image_id,
                scan_type=scan.scan_type,
                status=scan.status,
                started_at=scan.started_at,
                completed_at=scan.completed_at,
                vulnerabilities_count=scan.vulnerabilities_count,
                critical_count=scan.critical_count,
                high_count=scan.high_count,
                medium_count=scan.medium_count,
                low_count=scan.low_count,
            ),
            vulnerabilities=[
                ImageVulnerability(
                    id=v.id,
                    scan_id=v.scan_id,
                    name=v.name,
                    description=v.description,
                    severity=v.severity,
                    package_name=v.package_name,
                    package_version=v.package_version,
                    fixed_version=v.fixed_version,
                    reference_urls=v.reference_urls,
                    cve_id=v.cve_id,
                )
                for v in vulnerabilities
            ],
        )

        return scan_result
    except Exception as e:
        logger.error(f"Failed to scan image: {e}")
        raise


async def get_image_scans(image_id: str, db: Session = None) -> List[ImageScan]:
    """
    Get all scans for an image.
    """
    try:
        # Get image from database
        db_image = db.query(ImageModel).filter(ImageModel.docker_id == image_id).first()
        if not db_image:
            return []

        # Get scans
        scans = db.query(SecurityScan).filter(SecurityScan.image_id == db_image.id).all()

        # Convert to ImageScan objects
        return [
            ImageScan(
                id=scan.id,
                image_id=scan.image_id,
                scan_type=scan.scan_type,
                status=scan.status,
                started_at=scan.started_at,
                completed_at=scan.completed_at,
                vulnerabilities_count=scan.vulnerabilities_count,
                critical_count=scan.critical_count,
                high_count=scan.high_count,
                medium_count=scan.medium_count,
                low_count=scan.low_count,
            )
            for scan in scans
        ]
    except Exception as e:
        logger.error(f"Failed to get image scans: {e}")
        raise


async def get_image_scan(image_id: str, scan_id: int, db: Session = None) -> Optional[ImageScanResult]:
    """
    Get a scan for an image by ID.
    """
    try:
        # Get image from database
        db_image = db.query(ImageModel).filter(ImageModel.docker_id == image_id).first()
        if not db_image:
            return None

        # Get scan
        scan = db.query(SecurityScan).filter(SecurityScan.id == scan_id, SecurityScan.image_id == db_image.id).first()
        if not scan:
            return None

        # Get vulnerabilities
        vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()

        # Convert to ImageScan and ImageVulnerability objects
        scan_result = ImageScanResult(
            scan=ImageScan(
                id=scan.id,
                image_id=scan.image_id,
                scan_type=scan.scan_type,
                status=scan.status,
                started_at=scan.started_at,
                completed_at=scan.completed_at,
                vulnerabilities_count=scan.vulnerabilities_count,
                critical_count=scan.critical_count,
                high_count=scan.high_count,
                medium_count=scan.medium_count,
                low_count=scan.low_count,
            ),
            vulnerabilities=[
                ImageVulnerability(
                    id=v.id,
                    scan_id=v.scan_id,
                    name=v.name,
                    description=v.description,
                    severity=v.severity,
                    package_name=v.package_name,
                    package_version=v.package_version,
                    fixed_version=v.fixed_version,
                    reference_urls=v.reference_urls,
                    cve_id=v.cve_id,
                )
                for v in vulnerabilities
            ],
        )

        return scan_result
    except Exception as e:
        logger.error(f"Failed to get image scan: {e}")
        raise


async def search_docker_hub(query: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    Search Docker Hub for images.
    """
    try:
        # In a real implementation, this would call the Docker Hub API
        # For now, we'll return mock data
        await asyncio.sleep(1)  # Simulate API call delay

        # Mock response
        results = [
            {
                "name": "nginx",
                "description": "Official Nginx web server image",
                "is_official": True,
                "star_count": 15000,
                "pull_count": 1000000000,
                "logo_url": "https://www.nginx.com/wp-content/uploads/2018/08/NGINX-logo-rgb-large.png",
            },
            {
                "name": "redis",
                "description": "Redis is an open source key-value store",
                "is_official": True,
                "star_count": 10000,
                "pull_count": 500000000,
                "logo_url": "https://redis.io/images/redis-white.png",
            },
            {
                "name": "postgres",
                "description": "The PostgreSQL object-relational database system",
                "is_official": True,
                "star_count": 9000,
                "pull_count": 400000000,
                "logo_url": "https://www.postgresql.org/media/img/about/press/elephant.png",
            },
            {
                "name": "ubuntu",
                "description": "Ubuntu is a Debian-based Linux operating system",
                "is_official": True,
                "star_count": 12000,
                "pull_count": 800000000,
                "logo_url": "https://assets.ubuntu.com/v1/29985a98-ubuntu-logo32.png",
            },
            {
                "name": "node",
                "description": "Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine",
                "is_official": True,
                "star_count": 11000,
                "pull_count": 700000000,
                "logo_url": "https://nodejs.org/static/images/logo.svg",
            },
        ]

        # Filter by query
        if query:
            results = [r for r in results if query.lower() in r["name"].lower() or query.lower() in r["description"].lower()]

        # Calculate pagination
        total = len(results)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = results[start:end]

        return {
            "results": paginated_results,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }
    except Exception as e:
        logger.error(f"Failed to search Docker Hub: {e}")
        raise


async def get_image_tags(image_name: str) -> List[str]:
    """
    Get available tags for an image from Docker Hub.
    """
    try:
        # In a real implementation, this would call the Docker Hub API
        # For now, we'll return mock data
        await asyncio.sleep(0.5)  # Simulate API call delay

        # Mock response
        if image_name == "nginx":
            return ["latest", "1.21", "1.20", "1.19", "alpine"]
        elif image_name == "redis":
            return ["latest", "6.2", "6.0", "5.0", "alpine"]
        elif image_name == "postgres":
            return ["latest", "14", "13", "12", "alpine"]
        elif image_name == "ubuntu":
            return ["latest", "20.04", "18.04", "16.04"]
        elif image_name == "node":
            return ["latest", "16", "14", "12", "alpine"]
        else:
            return ["latest"]
    except Exception as e:
        logger.error(f"Failed to get image tags: {e}")
        raise


async def validate_dockerfile(dockerfile_content: str) -> DockerfileValidation:
    """
    Validate a Dockerfile.

    Args:
        dockerfile_content: The content of the Dockerfile to validate

    Returns:
        DockerfileValidation: Validation result
    """
    try:
        # Get troubleshooter
        troubleshooter = get_troubleshooter()

        # Analyze Dockerfile
        result = troubleshooter.analyze_dockerfile(dockerfile_content)

        # Extract validation information from the analysis
        is_valid = True
        errors = []
        warnings = []
        suggestions = []

        # Parse the analysis to extract validation information
        analysis_text = result["analysis"].lower()

        # Check for errors
        if "error" in analysis_text or "invalid" in analysis_text:
            is_valid = False
            # Extract error messages (this is a simplified approach)
            for line in analysis_text.split("\n"):
                if "error" in line.lower() or "invalid" in line.lower():
                    errors.append(line.strip())

        # Check for warnings
        if "warning" in analysis_text or "caution" in analysis_text:
            for line in analysis_text.split("\n"):
                if "warning" in line.lower() or "caution" in line.lower():
                    warnings.append(line.strip())

        # Check for suggestions
        if "suggestion" in analysis_text or "recommend" in analysis_text or "best practice" in analysis_text:
            for line in analysis_text.split("\n"):
                if "suggestion" in line.lower() or "recommend" in line.lower() or "best practice" in line.lower():
                    suggestions.append(line.strip())

        return DockerfileValidation(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            analysis=result["analysis"],
            provider=result["provider"],
            model=result["model"]
        )
    except Exception as e:
        logger.error(f"Failed to validate Dockerfile: {e}")
        raise


async def build_image_from_dockerfile(
    dockerfile: str,
    name: str,
    tag: str = "latest",
    options: Dict[str, Any] = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Build a Docker image from a Dockerfile.

    Args:
        dockerfile: The content of the Dockerfile
        name: The name of the image
        tag: The tag of the image
        options: Build options
        db: Database session

    Returns:
        Dict[str, Any]: Build result
    """
    try:
        # Create a temporary directory for the build context
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write the Dockerfile to the temporary directory
            dockerfile_path = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile)

            # Prepare build options
            build_options = options or {}
            no_cache = build_options.get("no_cache", False)
            pull = build_options.get("pull", False)

            # Build the image
            image_tag = f"{name}:{tag}"
            build_logs = []

            # Log the build start
            build_logs.append(f"Building image {image_tag}...")
            build_logs.append(f"Build context: {temp_dir}")

            # In a real implementation, this would call the Docker API to build the image
            # For now, we'll simulate the build process
            await asyncio.sleep(1)  # Simulate build time

            # Add build logs
            build_logs.append(f"Step 1/8 : FROM {name}:{tag}")
            build_logs.append(f"Step 2/8 : WORKDIR /app")
            build_logs.append(f"Step 3/8 : COPY . .")
            build_logs.append(f"Step 4/8 : RUN echo 'Building...'")
            build_logs.append(f"Step 5/8 : EXPOSE 80")
            build_logs.append(f"Step 6/8 : ENV NODE_ENV=production")
            build_logs.append(f"Step 7/8 : CMD [\"npm\", \"start\"]")
            build_logs.append(f"Step 8/8 : HEALTHCHECK CMD curl --fail http://localhost:80/ || exit 1")
            build_logs.append(f"Successfully built image {image_tag}")

            # Get the built image
            # In a real implementation, this would get the actual built image
            # For now, we'll create a mock image object
            image_data = {
                "id": "sha256:1234567890abcdef",
                "short_id": "1234567890ab",
                "tags": [image_tag],
                "size": 150000000,  # 150MB
                "created_at": datetime.now().isoformat(),
                "docker_id": "sha256:1234567890abcdef",
                "digest": "sha256:1234567890abcdef",
                "name": name,
                "tag": tag,
                "author": "DockerForge",
                "architecture": "amd64",
                "os": "linux",
                "labels": {"org.opencontainers.image.created": datetime.now().isoformat()}
            }

            return {
                "success": True,
                "image": image_data,
                "logs": build_logs,
                "message": f"Successfully built image {image_tag}"
            }
    except Exception as e:
        logger.error(f"Failed to build image: {e}")
        raise
