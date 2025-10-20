"""
API Request Models
Defines the structure of data clients send to the API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class QueryRequest(BaseModel):
    """General query request"""
    query: str = Field(..., description="User's question or request", min_length=1)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the food safety requirements for restaurants?",
                "context": {"restaurant_name": "Chef India"}
            }
        }


class BusinessQueryRequest(BaseModel):
    """Business operations query request"""
    query: str = Field(..., description="Business-related question", min_length=1)
    restaurant_name: Optional[str] = Field(None, description="Specific restaurant to analyze")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional business context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "My chicken is expiring today, what items should I discount?",
                "restaurant_name": "Chef India"
            }
        }


class ComplianceQueryRequest(BaseModel):
    """Compliance analysis query request"""
    query: str = Field(..., description="Compliance-related question", min_length=1)
    restaurant_name: Optional[str] = Field(None, description="Specific restaurant to analyze")
    standards: Optional[List[str]] = Field(
        default=["HACCP", "Food Safety"],
        description="Compliance standards to check against"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How can I make my menu HACCP compliant?",
                "restaurant_name": "Chef India",
                "standards": ["HACCP", "Food Safety"]
            }
        }


class SearchRequest(BaseModel):
    """Search menu items request"""
    query: str = Field(..., description="Search query", min_length=1)
    restaurant_name: Optional[str] = Field(None, description="Search in specific restaurant only")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "chicken",
                "restaurant_name": "Chef India"
            }
        }


class MenuUploadRequest(BaseModel):
    """Menu upload metadata (file sent separately as multipart)"""
    restaurant_name: str = Field(..., description="Name of the restaurant", min_length=1)
    description: Optional[str] = Field(None, description="Optional menu description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_name": "Chef India",
                "description": "Main dinner menu"
            }
        }



