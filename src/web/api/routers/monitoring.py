"""
Monitoring router for the DockerForge Web UI.

This module provides API endpoints for AI monitoring, resource monitoring, and troubleshooting.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Path
from datetime import datetime, timedelta

from src.web.api.schemas import monitoring as schemas
from src.config.config_manager import get_config
from src.core.ai_provider import get_ai_provider, AIProviderFactory, AIProviderError
from src.core.ai_usage_tracker import AIUsageTracker
from src.core.troubleshooter import get_troubleshooter, TroubleshooterError
from src.web.api.services import host_stats, alerts

router = APIRouter()


# Host Metrics Endpoints

@router.get("/host/metrics", response_model=schemas.HostMetrics)
async def get_host_metrics():
    """
    Get current host metrics.
    """
    try:
        # Get host metrics
        metrics = await host_stats.get_host_metrics()

        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting host metrics: {str(e)}"
        )


@router.get("/host/metrics/history/{metric_type}", response_model=List[Dict[str, Any]])
async def get_host_metrics_history(
    metric_type: str = Path(..., description="Metric type (cpu, memory, disk, network)"),
    hours: int = Query(1, ge=1, le=24, description="Number of hours of history to retrieve")
):
    """
    Get historical host metrics.
    """
    try:
        # Validate metric type
        if metric_type not in ["cpu", "memory", "disk", "network"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metric type: {metric_type}. Must be one of: cpu, memory, disk, network"
            )

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Get metrics history
        metrics = await host_stats.get_host_metrics_history(metric_type, start_time, end_time)

        return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting host metrics history: {str(e)}"
        )


@router.get("/host/system-info", response_model=schemas.SystemInfo)
async def get_system_info():
    """
    Get system information.
    """
    try:
        # Get system information
        system_info = await host_stats.get_system_info()

        return system_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system information: {str(e)}"
        )


@router.get("/host/stats-summary", response_model=schemas.ResourceStatsSummary)
async def get_resource_stats_summary():
    """
    Get resource stats summary.
    """
    try:
        # Get resource stats summary
        summary = await host_stats.get_resource_stats_summary()

        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting resource stats summary: {str(e)}"
        )


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


# Alerts Endpoints

@router.get("/alerts", response_model=List[schemas.Alert])
async def get_alerts():
    """
    Get all active alerts.
    """
    try:
        # Get alerts
        active_alerts = await alerts.get_active_alerts()

        return active_alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting alerts: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge an alert.
    """
    try:
        # Acknowledge alert
        await alerts.acknowledge_alert(alert_id)

        return {"status": "success", "message": f"Alert {alert_id} acknowledged"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acknowledging alert: {str(e)}"
        )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """
    Resolve an alert.
    """
    try:
        # Resolve alert
        await alerts.resolve_alert(alert_id)

        return {"status": "success", "message": f"Alert {alert_id} resolved"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving alert: {str(e)}"
        )
