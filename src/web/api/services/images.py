"""
Image service for the DockerForge Web UI.

This module provides the image management services for the DockerForge Web UI.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from src.web.api.schemas.images import Image, ImageCreate, ImageUpdate, ImageScan, ImageVulnerability, ImageScanResult
from src.web.api.services import docker
from src.web.api.models.image import Image as ImageModel, SecurityScan, Vulnerability

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
