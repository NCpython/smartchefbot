"""
API Response Models
Defines the structure of data the API returns to clients
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Always false for errors")
    error_code: str = Field(..., description="Machine-readable error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "MENU_NOT_FOUND",
                "error_message": "Restaurant 'ABC' not found",
                "details": {"available_restaurants": ["Chef", "CCD"]}
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class QueryResponse(BaseModel):
    """General query response"""
    success: bool = Field(..., description="Query success status")
    response: str = Field(..., description="AI-generated response")
    iterations_used: Optional[int] = Field(None, description="Number of agent iterations used")
    scratchpad: Optional[List[str]] = Field(None, description="Agent's thinking process")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Food safety requirements include maintaining proper temperatures...",
                "iterations_used": 2,
                "scratchpad": ["Iteration 1: Processing query", "Iteration 2: Generated response"]
            }
        }


class BusinessResponse(BaseModel):
    """Business operations response"""
    success: bool = Field(..., description="Query success status")
    response: str = Field(..., description="Business recommendations")
    menu_items_analyzed: int = Field(..., description="Number of menu items analyzed")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Structured recommendations")
    iterations_used: Optional[int] = Field(None, description="Agent iterations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Here are my recommendations for your expiring chicken...",
                "menu_items_analyzed": 12,
                "recommendations": [
                    {"item": "Butter Chicken", "action": "Discount 30%", "reason": "High demand"}
                ]
            }
        }


class ComplianceResponse(BaseModel):
    """Compliance analysis response"""
    success: bool = Field(..., description="Analysis success status")
    response: str = Field(..., description="Compliance recommendations")
    menu_items_analyzed: int = Field(..., description="Number of items analyzed")
    compliance_issues: Optional[List[Dict[str, Any]]] = Field(None, description="Identified issues")
    compliance_score: Optional[float] = Field(None, description="Overall compliance score (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response": "Your menu needs the following HACCP improvements...",
                "menu_items_analyzed": 12,
                "compliance_score": 75.5
            }
        }


class MenuItemResponse(BaseModel):
    """Single menu item response"""
    name: str = Field(..., description="Item name")
    price: Optional[str] = Field(None, description="Item price in Euros")
    description: Optional[str] = Field(None, description="Item description")
    category: Optional[str] = Field(None, description="Item category")
    restaurant: Optional[str] = Field(None, description="Restaurant name")


class MenuResponse(BaseModel):
    """Single restaurant menu response"""
    success: bool = Field(..., description="Request success status")
    restaurant_name: str = Field(..., description="Restaurant name")
    items: List[MenuItemResponse] = Field(..., description="Menu items")
    total_items: int = Field(..., description="Total number of items")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "restaurant_name": "Chef India",
                "items": [
                    {"name": "Butter Chicken", "price": "€12.99", "description": "Creamy curry"}
                ],
                "total_items": 12
            }
        }


class MenuListResponse(BaseModel):
    """List of all menus response"""
    success: bool = Field(..., description="Request success status")
    menus: List[Dict[str, Any]] = Field(..., description="List of restaurant menus")
    count: int = Field(..., description="Total number of menus")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "menus": [
                    {"restaurant_name": "Chef India", "total_items": 12},
                    {"restaurant_name": "CCD", "total_items": 8}
                ],
                "count": 2
            }
        }


class SearchResponse(BaseModel):
    """Search results response"""
    success: bool = Field(..., description="Search success status")
    query: str = Field(..., description="Original search query")
    results: List[MenuItemResponse] = Field(..., description="Matching menu items")
    count: int = Field(..., description="Number of results found")
    searched_restaurants: Optional[List[str]] = Field(None, description="Restaurants searched")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "chicken",
                "results": [
                    {"name": "Butter Chicken", "price": "€12.99", "restaurant": "Chef India"}
                ],
                "count": 3,
                "searched_restaurants": ["Chef India", "CCD"]
            }
        }


class SystemHealthResponse(BaseModel):
    """System health check response"""
    status: str = Field(..., description="System status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    uptime: Optional[float] = Field(None, description="Uptime in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "SmartChefBot",
                "version": "1.0.0",
                "uptime": 3600.5
            }
        }


class SystemStatsResponse(BaseModel):
    """System statistics response"""
    success: bool = Field(..., description="Request success status")
    total_menus: int = Field(..., description="Total menus uploaded")
    total_items: int = Field(..., description="Total menu items across all menus")
    restaurants: List[str] = Field(..., description="List of restaurant names")
    storage_used: Optional[str] = Field(None, description="Storage space used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_menus": 5,
                "total_items": 67,
                "restaurants": ["Chef India", "CCD", "Chef", "allowme", "clear"],
                "storage_used": "2.4 MB"
            }
        }



