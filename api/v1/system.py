"""
System API Router
Handles system health, statistics, and administrative operations
"""

from fastapi import APIRouter, HTTPException, status
import sys
from pathlib import Path
import time
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.responses import (
    SystemHealthResponse,
    SystemStatsResponse,
    SuccessResponse,
    ErrorResponse
)

# Lazy import to avoid blocking server startup
def get_menu_tool():
    """Lazy load menu_tool only when needed"""
    from tool.menu_tool import menu_tool
    return menu_tool

# Create router
router = APIRouter(
    prefix="/api/v1/system",
    tags=["System"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

# Track server start time
SERVER_START_TIME = time.time()


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    summary="Health check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        - Service status
        - Service name
        - API version
        - Uptime in seconds
        
    Example:
        ```
        GET /api/v1/system/health
        ```
    """
    try:
        uptime = time.time() - SERVER_START_TIME
        
        return SystemHealthResponse(
            status="healthy",
            service="SmartChefBot API",
            version="1.0.0",
            uptime=round(uptime, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=SystemStatsResponse,
    summary="Get system statistics",
    description="Get statistics about uploaded menus and system usage"
)
async def get_system_stats():
    """
    Get system statistics including menu counts and storage usage.
    
    Returns:
        - Total number of menus
        - Total menu items across all menus
        - List of restaurant names
        - Storage space used (optional)
        
    Example:
        ```
        GET /api/v1/system/stats
        ```
    """
    try:
        # Get all menus
        menus = get_menu_tool().list_menus()
        
        # Calculate total items
        total_items = sum(menu.get('total_items', 0) for menu in menus)
        
        # Get restaurant names
        restaurants = [menu.get('restaurant_name', 'Unknown') for menu in menus]
        
        # Calculate storage used (optional)
        storage_used = None
        try:
            data_dir = Path(__file__).parent.parent.parent / "data"
            if data_dir.exists():
                total_size = sum(
                    f.stat().st_size 
                    for f in data_dir.rglob('*') 
                    if f.is_file()
                )
                # Convert to human-readable format
                if total_size < 1024:
                    storage_used = f"{total_size} B"
                elif total_size < 1024 * 1024:
                    storage_used = f"{total_size / 1024:.1f} KB"
                else:
                    storage_used = f"{total_size / (1024 * 1024):.1f} MB"
        except Exception:
            pass  # Storage calculation is optional
        
        return SystemStatsResponse(
            success=True,
            total_menus=len(menus),
            total_items=total_items,
            restaurants=restaurants,
            storage_used=storage_used
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system stats: {str(e)}"
        )


@router.post(
    "/clear",
    response_model=SuccessResponse,
    summary="Clear all data",
    description="Clear all uploaded menus and extracted data (CAUTION: Cannot be undone!)"
)
async def clear_all_data():
    """
    Clear all menu data from the system.
    
    ⚠️ WARNING: This operation cannot be undone!
    
    This will delete:
    - All uploaded PDF files
    - All extracted JSON data
    - All menu items
    
    Returns:
        - Success status
        - Confirmation message
        
    Example:
        ```
        POST /api/v1/system/clear
        ```
    """
    try:
        # Clear all data using menu tool
        success = get_menu_tool().clear_all_data()
        
        if success:
            return SuccessResponse(
                success=True,
                message="All menu data cleared successfully",
                data={
                    "cleared_menus": True,
                    "cleared_pdfs": True
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear data"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clear operation failed: {str(e)}"
        )


@router.get(
    "/version",
    summary="Get API version",
    description="Get the current API version information"
)
async def get_version():
    """
    Get API version information.
    
    Returns:
        - API version
        - Service name
        - Build information
        
    Example:
        ```
        GET /api/v1/system/version
        ```
    """
    return {
        "service": "SmartChefBot API",
        "version": "1.0.0",
        "api_version": "v1",
        "description": "AI-powered restaurant intelligence and compliance assistant"
    }



