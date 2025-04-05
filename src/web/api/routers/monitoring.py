"""
Monitoring router for the DockerForge Web UI.

This module provides API endpoints for AI monitoring and troubleshooting.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime

from src.web.api.database import get_db
from src.web.api.schemas import monitoring as schemas
from src.config.config_manager import get_config
from src.core.ai_provider import get_ai_provider, AIProviderFactory, AIProviderError
from src.core.ai_usage_tracker import AIUsageTracker
from src.core.troubleshooter import get_troubleshooter, TroubleshooterError

router = APIRouter()


@router.get("/ai-status", response_model=schemas.AIStatusResponse)
async def get_ai_status():
    """
    Get the status of all AI providers.
    """
    try:
        # Get available providers
        providers_info = AIProviderFactory.list_available_providers()

        # Get default provider
        default_provider = get_config("ai.default_provider", "ollama")

        # Convert to response format
        providers_status = {}
        for name, info in providers_info.items():
            # Try to get capabilities if provider is enabled
            capabilities = None
            if info.get("enabled", False):
                try:
                    provider = get_ai_provider(name)
                    capabilities = provider.report_capabilities()
                except AIProviderError:
                    pass

            providers_status[name] = schemas.AIProviderStatus(
                name=name,
                enabled=info.get("enabled", False),
                available=info.get("available", False),
                type=info.get("type", "unknown"),
                version=info.get("version"),
                author=info.get("author"),
                description=info.get("description"),
                capabilities=schemas.AICapabilities(**capabilities) if capabilities else None
            )

        return schemas.AIStatusResponse(
            providers=providers_status,
            default_provider=default_provider
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI status: {str(e)}"
        )


@router.get("/ai-usage", response_model=schemas.AIUsageReport)
async def get_ai_usage():
    """
    Get AI usage statistics.
    """
    try:
        # Initialize usage tracker
        usage_tracker = AIUsageTracker()

        # Get usage report
        report = usage_tracker.get_usage_report()

        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI usage: {str(e)}"
        )


@router.post("/troubleshoot/container/{container_id}", response_model=schemas.ContainerTroubleshootingResult)
async def troubleshoot_container(
    container_id: str,
    request: schemas.ContainerTroubleshootingRequest
):
    """
    Analyze a container using AI.
    """
    try:
        # Get troubleshooter
        troubleshooter = get_troubleshooter()

        # Analyze container
        result = troubleshooter.analyze_container(
            container_id=container_id,
            confirm_cost=request.confirm_cost
        )

        return schemas.ContainerTroubleshootingResult(
            container_id=result["container_id"],
            container_name=result["container_name"],
            container_status=result["container_status"],
            analysis=result["analysis"],
            provider=result["provider"],
            model=result["model"],
            timestamp=datetime.now()
        )
    except TroubleshooterError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing container: {str(e)}"
        )


@router.post("/troubleshoot/logs", response_model=schemas.TroubleshootingResult)
async def troubleshoot_logs(
    request: schemas.LogsTroubleshootingRequest
):
    """
    Analyze logs using AI.
    """
    try:
        # Get troubleshooter
        troubleshooter = get_troubleshooter()

        # Analyze logs
        result = troubleshooter.analyze_logs(request.logs)

        return schemas.TroubleshootingResult(
            analysis=result["analysis"],
            provider=result["provider"],
            model=result["model"],
            timestamp=datetime.now()
        )
    except TroubleshooterError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing logs: {str(e)}"
        )


@router.post("/troubleshoot/compose", response_model=schemas.TroubleshootingResult)
async def troubleshoot_compose(
    request: schemas.DockerComposeRequest
):
    """
    Analyze a Docker Compose file using AI.
    """
    try:
        # Get troubleshooter
        troubleshooter = get_troubleshooter()

        # Analyze Docker Compose file
        result = troubleshooter.analyze_docker_compose(request.content)

        return schemas.TroubleshootingResult(
            analysis=result["analysis"],
            provider=result["provider"],
            model=result["model"],
            timestamp=datetime.now()
        )
    except TroubleshooterError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing Docker Compose file: {str(e)}"
        )


@router.post("/troubleshoot/dockerfile", response_model=schemas.TroubleshootingResult)
async def troubleshoot_dockerfile(
    request: schemas.DockerfileRequest
):
    """
    Analyze a Dockerfile using AI.
    """
    try:
        # Get troubleshooter
        troubleshooter = get_troubleshooter()

        # Analyze Dockerfile
        result = troubleshooter.analyze_dockerfile(request.content)

        return schemas.TroubleshootingResult(
            analysis=result["analysis"],
            provider=result["provider"],
            model=result["model"],
            timestamp=datetime.now()
        )
    except TroubleshooterError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing Dockerfile: {str(e)}"
        )


@router.get("/troubleshoot/connection", response_model=schemas.ConnectionTroubleshootingResult)
async def troubleshoot_connection():
    """
    Check Docker connection and troubleshoot issues.
    """
    try:
        # Get troubleshooter
        troubleshooter = get_troubleshooter()

        # Troubleshoot connection
        result = troubleshooter.troubleshoot_connection()

        return schemas.ConnectionTroubleshootingResult(
            connected=result["connected"],
            issues=result["issues"],
            fixes=result["fixes"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error troubleshooting connection: {str(e)}"
        )
