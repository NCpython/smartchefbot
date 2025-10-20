"""
Items API Router
Handles menu item search and retrieval operations
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.requests import SearchRequest
from api.models.responses import SearchResponse, MenuItemResponse, ErrorResponse
from tool.menu_tool import menu_tool

# Create router
router = APIRouter(
    prefix="/api/v1/items",
    tags=["Items"],
    responses={
        404: {"model": ErrorResponse, "description": "Items not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search menu items across all restaurants",
    description="Search for menu items across all uploaded menus or in a specific restaurant"
)
async def search_menu_items(request: SearchRequest):
    """
    Search for menu items across all restaurants or in a specific restaurant.
    
    Args:
        - query: Search query string
        - restaurant_name (optional): Search only in this restaurant
        - filters (optional): Additional search filters
        
    Returns:
        - List of matching menu items
        - Total count of results
        - Restaurants searched
        
    Example:
        ```json
        POST /api/v1/items/search
        {
            "query": "chicken",
            "restaurant_name": "Chef India"
        }
        ```
    """
    try:
        all_results = []
        searched_restaurants = []
        
        if request.restaurant_name:
            # Search in specific restaurant
            results = menu_tool.search_menu_items(request.restaurant_name, request.query)
            searched_restaurants.append(request.restaurant_name)
            
            # Add restaurant name to each result
            for item in results:
                item['restaurant'] = request.restaurant_name
                all_results.append(item)
        else:
            # Search across all restaurants
            all_menus = menu_tool.list_all_menus()
            searched_restaurants = all_menus
            
            for restaurant in all_menus:
                results = menu_tool.search_menu_items(restaurant, request.query)
                
                # Add restaurant name to each result
                for item in results:
                    item['restaurant'] = restaurant
                    all_results.append(item)
        
        # Convert to response models
        items = [MenuItemResponse(**item) for item in all_results]
        
        return SearchResponse(
            success=True,
            query=request.query,
            results=items,
            count=len(items),
            searched_restaurants=searched_restaurants
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get(
    "/search/{query}",
    response_model=SearchResponse,
    summary="Search menu items (GET method)",
    description="Search for menu items using GET method for simple queries"
)
async def search_menu_items_get(
    query: str,
    restaurant_name: Optional[str] = None
):
    """
    Search for menu items using GET method.
    
    This is a convenience endpoint for simple searches without needing POST.
    
    Args:
        - query: Search query string (in URL path)
        - restaurant_name (optional): Query parameter to search in specific restaurant
        
    Returns:
        - List of matching menu items
        - Total count of results
        
    Example:
        ```
        GET /api/v1/items/search/chicken?restaurant_name=Chef%20India
        ```
    """
    # Create a SearchRequest and delegate to POST handler
    request = SearchRequest(query=query, restaurant_name=restaurant_name)
    return await search_menu_items(request)


@router.get(
    "/{restaurant_name}/search",
    response_model=SearchResponse,
    summary="Search items in specific restaurant",
    description="Search for menu items within a specific restaurant"
)
async def search_in_restaurant(
    restaurant_name: str,
    query: str
):
    """
    Search for menu items in a specific restaurant.
    
    Args:
        - restaurant_name: Restaurant to search in (URL path)
        - query: Search query (query parameter)
        
    Returns:
        - Matching items from the specified restaurant
        
    Example:
        ```
        GET /api/v1/items/Chef%20India/search?query=chicken
        ```
    """
    try:
        # Check if restaurant exists
        menu_data = menu_tool.load_menu_data(restaurant_name)
        if not menu_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurant '{restaurant_name}' not found"
            )
        
        # Search in this restaurant
        results = menu_tool.search_menu_items(restaurant_name, query)
        
        # Add restaurant name to results
        for item in results:
            item['restaurant'] = restaurant_name
        
        # Convert to response models
        items = [MenuItemResponse(**item) for item in results]
        
        return SearchResponse(
            success=True,
            query=query,
            results=items,
            count=len(items),
            searched_restaurants=[restaurant_name]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )



