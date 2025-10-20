"""
Menus API Router
Handles all menu management operations
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.requests import SearchRequest
from api.models.responses import (
    MenuResponse, 
    MenuListResponse, 
    SuccessResponse, 
    ErrorResponse,
    MenuItemResponse
)
from tool.menu_tool import menu_tool

# Create router
router = APIRouter(
    prefix="/api/v1/menus",
    tags=["Menus"],
    responses={
        404: {"model": ErrorResponse, "description": "Menu not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=MenuListResponse,
    summary="List all restaurant menus",
    description="Get a list of all uploaded restaurant menus with item counts"
)
async def list_all_menus():
    """
    List all uploaded restaurant menus.
    
    Returns:
        - List of restaurants with their menu data
        - Total count of menus
        
    Example:
        ```
        GET /api/v1/menus/
        ```
    """
    try:
        menus = menu_tool.list_menus()
        
        return MenuListResponse(
            success=True,
            menus=menus,
            count=len(menus)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/upload",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a menu PDF",
    description="Upload and process a restaurant menu PDF using Gemini AI"
)
async def upload_menu(
    file: UploadFile = File(..., description="PDF file to upload"),
    restaurant_name: str = Form(..., description="Name of the restaurant")
):
    """
    Upload a menu PDF and extract menu items using Gemini AI.
    
    Args:
        - file: PDF file (multipart/form-data)
        - restaurant_name: Restaurant name
        
    Returns:
        - Success status
        - Number of items extracted
        
    Example:
        ```
        POST /api/v1/menus/upload
        Content-Type: multipart/form-data
        
        file: <menu.pdf>
        restaurant_name: "Chef India"
        ```
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Save uploaded file temporarily
        upload_dir = Path(__file__).parent.parent.parent / "data" / "menus"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{restaurant_name}.pdf"
        
        # Write file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with menu tool (uses Gemini AI)
        result = menu_tool.upload_menu(str(file_path), restaurant_name)
        
        if result['success']:
            return SuccessResponse(
                success=True,
                message=f"Successfully processed PDF with Gemini! Extracted {result['item_count']} menu items.",
                data={
                    "restaurant_name": restaurant_name,
                    "item_count": result['item_count']
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract menu: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get(
    "/{restaurant_name}",
    response_model=MenuResponse,
    summary="Get specific restaurant menu",
    description="Get all menu items for a specific restaurant"
)
async def get_restaurant_menu(
    restaurant_name: str,
):
    """
    Get menu data for a specific restaurant.
    
    Args:
        - restaurant_name: Name of the restaurant
        
    Returns:
        - Restaurant name
        - List of all menu items
        - Total item count
        
    Example:
        ```
        GET /api/v1/menus/Chef%20India
        ```
    """
    try:
        # Load menu data
        menu_data = menu_tool.load_menu_data(restaurant_name)
        
        if not menu_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurant '{restaurant_name}' not found"
            )
        
        # Convert items to response model
        items = [MenuItemResponse(**item) for item in menu_data.get('items', [])]
        
        return MenuResponse(
            success=True,
            restaurant_name=restaurant_name,
            items=items,
            total_items=len(items)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{restaurant_name}",
    response_model=SuccessResponse,
    summary="Delete a restaurant menu",
    description="Delete all data for a specific restaurant"
)
async def delete_restaurant_menu(restaurant_name: str):
    """
    Delete a restaurant's menu data.
    
    Args:
        - restaurant_name: Name of the restaurant to delete
        
    Returns:
        - Success status
        - Confirmation message
        
    Example:
        ```
        DELETE /api/v1/menus/Chef%20India
        ```
    """
    try:
        # Check if menu exists
        menu_data = menu_tool.load_menu_data(restaurant_name)
        
        if not menu_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurant '{restaurant_name}' not found"
            )
        
        # Delete JSON file
        extracted_dir = Path(__file__).parent.parent.parent / "data" / "extracted"
        json_file = extracted_dir / f"{restaurant_name}.json"
        if json_file.exists():
            json_file.unlink()
        
        # Delete PDF file
        menus_dir = Path(__file__).parent.parent.parent / "data" / "menus"
        pdf_file = menus_dir / f"{restaurant_name}.pdf"
        if pdf_file.exists():
            pdf_file.unlink()
        
        return SuccessResponse(
            success=True,
            message=f"Successfully deleted menu for '{restaurant_name}'",
            data={"restaurant_name": restaurant_name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )


@router.get(
    "/{restaurant_name}/items",
    response_model=MenuResponse,
    summary="Get all items from a restaurant",
    description="Get detailed list of all menu items for a specific restaurant"
)
async def get_restaurant_items(restaurant_name: str):
    """
    Get all menu items for a specific restaurant.
    
    This is an alias for GET /menus/{restaurant_name} but more RESTful.
    
    Args:
        - restaurant_name: Name of the restaurant
        
    Returns:
        - List of all menu items with details
        
    Example:
        ```
        GET /api/v1/menus/Chef%20India/items
        ```
    """
    # Reuse the get_restaurant_menu logic
    return await get_restaurant_menu(restaurant_name)



