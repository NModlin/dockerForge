"""
Compose Templates router for the DockerForge Web UI.

This module provides the API endpoints for Docker Compose template management.
"""

import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from src.compose.template_manager import TemplateManager
from src.config.config_manager import get_config
from src.core.ai_provider import get_ai_provider
from src.utils.logging_manager import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/compose/templates",
    tags=["compose-templates"],
    responses={404: {"description": "Not found"}},
)

# Get template manager instance
template_manager = TemplateManager()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_templates(category: Optional[str] = None):
    """
    List available templates.

    Args:
        category: Optional category to filter by

    Returns:
        List of template dictionaries with metadata
    """
    try:
        templates = template_manager.list_templates(category)
        return templates
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}",
        )


@router.get("/categories", response_model=List[str])
async def get_categories():
    """
    Get all template categories.

    Returns:
        List of category names
    """
    try:
        categories = template_manager.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Failed to get categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categories: {str(e)}",
        )


@router.get("/by-category", response_model=Dict[str, List[Dict[str, Any]]])
async def get_templates_by_category():
    """
    Get templates organized by category.

    Returns:
        Dictionary mapping category names to lists of template info dictionaries
    """
    try:
        templates_by_category = template_manager.get_templates_by_category()
        return templates_by_category
    except Exception as e:
        logger.error(f"Failed to get templates by category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates by category: {str(e)}",
        )


@router.get("/{template_name}", response_model=Dict[str, Any])
async def get_template(
    template_name: str = Path(..., description="Name of the template")
):
    """
    Get a template by name.

    Args:
        template_name: Name of the template

    Returns:
        Template dictionary
    """
    try:
        template = template_manager.get_template(template_name)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_name} not found",
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template {template_name}: {str(e)}",
        )


@router.get("/{template_name}/content", response_model=Dict[str, str])
async def get_template_content(
    template_name: str = Path(..., description="Name of the template")
):
    """
    Get the content of a template.

    Args:
        template_name: Name of the template

    Returns:
        Dictionary with template content
    """
    try:
        template = template_manager.get_template(template_name)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_name} not found",
            )

        import yaml

        content = yaml.dump(template, default_flow_style=False, sort_keys=False)
        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template content for {template_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template content for {template_name}: {str(e)}",
        )


@router.post("/{template_name}/customize", response_model=Dict[str, str])
async def customize_template(
    template_name: str = Path(..., description="Name of the template"),
    data: Dict[str, str] = Body(..., description="Customization data"),
):
    """
    Customize a template using AI.

    Args:
        template_name: Name of the template
        data: Dictionary with customization instructions

    Returns:
        Dictionary with customized template content
    """
    try:
        instructions = data.get("instructions")
        if not instructions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customization instructions are required",
            )

        # Get AI provider
        ai_provider = get_ai_provider()

        # Customize template
        customized_template = template_manager.customize_template_with_ai(
            template_name, instructions, ai_provider
        )

        # Convert to YAML
        import yaml

        content = yaml.dump(
            customized_template, default_flow_style=False, sort_keys=False
        )

        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to customize template {template_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to customize template {template_name}: {str(e)}",
        )


@router.post("/import", response_model=Dict[str, str])
async def import_template(
    file: UploadFile = File(..., description="Template file"),
    name: Optional[str] = Form(None, description="Template name"),
    category: Optional[str] = Form("custom", description="Template category"),
):
    """
    Import a template from a file.

    Args:
        file: Template file
        name: Optional template name
        category: Optional template category

    Returns:
        Dictionary with import result
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            # Write uploaded file to temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Import template
            template_name = template_manager.import_template(
                temp_file_path, name, category
            )

            # Remove temporary file
            os.unlink(temp_file_path)

            return {"message": f"Template {template_name} imported successfully"}
        finally:
            # Ensure temporary file is removed
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        logger.error(f"Failed to import template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import template: {str(e)}",
        )


@router.post("/export/{template_name}", response_model=Dict[str, str])
async def export_template(
    template_name: str = Path(..., description="Name of the template")
):
    """
    Export a template to a file.

    Args:
        template_name: Name of the template

    Returns:
        Dictionary with export result
    """
    try:
        # Export template
        output_path = get_config(
            "general.export_dir", os.path.expanduser("~/.dockerforge/exports")
        )
        os.makedirs(output_path, exist_ok=True)

        file_path = template_manager.export_template(template_name, output_path)

        return {"message": f"Template {template_name} exported to {file_path}"}
    except Exception as e:
        logger.error(f"Failed to export template {template_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export template {template_name}: {str(e)}",
        )


@router.delete("/{template_name}", response_model=Dict[str, str])
async def delete_template(
    template_name: str = Path(..., description="Name of the template")
):
    """
    Delete a template.

    Args:
        template_name: Name of the template

    Returns:
        Dictionary with deletion result
    """
    try:
        # Delete template
        result = template_manager.delete_template(template_name)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_name} not found",
            )

        return {"message": f"Template {template_name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template {template_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template {template_name}: {str(e)}",
        )
