"""
Query API Router
Handles AI query processing for general questions, business operations, and compliance
"""

from fastapi import APIRouter, HTTPException, status
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.requests import QueryRequest, BusinessQueryRequest, ComplianceQueryRequest
from api.models.responses import (
    QueryResponse, 
    BusinessResponse, 
    ComplianceResponse, 
    ErrorResponse
)
from agent.executor import executor

# Create router
router = APIRouter(
    prefix="/api/v1/query",
    tags=["Query"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post(
    "/general",
    response_model=QueryResponse,
    summary="Process general queries",
    description="Ask general questions about restaurant operations, food safety, and compliance"
)
async def process_general_query(request: QueryRequest):
    """
    Process a general query using the AI agent.
    
    This endpoint handles:
    - General restaurant questions
    - Food safety queries
    - Compliance information
    - Menu-related questions
    
    Args:
        - query: Your question
        - context (optional): Additional context
        
    Returns:
        - AI-generated response
        - Agent iterations used
        - Thinking process (scratchpad)
        
    Example:
        ```json
        POST /api/v1/query/general
        {
            "query": "What are the food safety requirements for restaurants?"
        }
        ```
    """
    try:
        # Process query through executor
        result = executor.run(request.query, context=request.context)
        
        if result['success']:
            return QueryResponse(
                success=True,
                response=result['response'],
                iterations_used=result.get('iterations_used'),
                scratchpad=result.get('scratchpad'),
                metadata={
                    'max_iterations': result.get('max_iterations'),
                    'query_type': 'general'
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Query processing failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing error: {str(e)}"
        )


@router.post(
    "/business",
    response_model=BusinessResponse,
    summary="Get business operations recommendations",
    description="Ask business-related questions and get recommendations based on your menu data"
)
async def process_business_query(request: BusinessQueryRequest):
    """
    Process a business operations query with menu data analysis.
    
    This endpoint uses HYBRID MODE:
    - Retrieves your actual menu data (Tool)
    - Applies AI business intelligence (LLM)
    - Provides specific, actionable recommendations
    
    Perfect for questions like:
    - "What items should I discount?"
    - "Which menu items use chicken?"
    - "How can I reduce waste?"
    - "What promotions should I run?"
    
    Args:
        - query: Your business question
        - restaurant_name (optional): Specific restaurant to analyze
        - context (optional): Additional business context
        
    Returns:
        - Business recommendations
        - Number of menu items analyzed
        - Structured recommendations
        
    Example:
        ```json
        POST /api/v1/query/business
        {
            "query": "My chicken is expiring today, what should I discount?",
            "restaurant_name": "Chef India"
        }
        ```
    """
    try:
        # Add restaurant context if specified
        context = request.context or {}
        if request.restaurant_name:
            context['restaurant_name'] = request.restaurant_name
        
        # Process through executor
        result = executor.run(request.query, context=context)
        
        if result['success']:
            # Count menu items analyzed (if available)
            menu_items_count = 0
            if 'scratchpad' in result:
                for note in result['scratchpad']:
                    if 'Retrieved' in note and 'items' in note:
                        # Try to extract count from scratchpad
                        import re
                        match = re.search(r'(\d+)\s+items', note)
                        if match:
                            menu_items_count = int(match.group(1))
                            break
            
            return BusinessResponse(
                success=True,
                response=result['response'],
                menu_items_analyzed=menu_items_count,
                recommendations=None,  # Could be structured in future
                iterations_used=result.get('iterations_used')
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Business query processing failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business query error: {str(e)}"
        )


@router.post(
    "/compliance",
    response_model=ComplianceResponse,
    summary="Get compliance analysis and recommendations",
    description="Analyze your menu for HACCP and food safety compliance"
)
async def process_compliance_query(request: ComplianceQueryRequest):
    """
    Process a compliance analysis query.
    
    This endpoint uses HYBRID MODE:
    - Analyzes your actual menu items (Tool)
    - Applies HACCP and food safety knowledge (LLM)
    - Provides specific compliance recommendations
    
    Perfect for questions like:
    - "How can I make my menu HACCP compliant?"
    - "What food safety issues should I address?"
    - "Do I need allergen warnings?"
    - "What temperature requirements apply?"
    
    Args:
        - query: Your compliance question
        - restaurant_name (optional): Specific restaurant to analyze
        - standards (optional): List of standards to check against
        
    Returns:
        - Compliance recommendations
        - Number of items analyzed
        - Identified compliance issues
        
    Example:
        ```json
        POST /api/v1/query/compliance
        {
            "query": "How can I make my menu HACCP compliant?",
            "restaurant_name": "Chef India",
            "standards": ["HACCP", "Food Safety"]
        }
        ```
    """
    try:
        # Add context
        context = {}
        if request.restaurant_name:
            context['restaurant_name'] = request.restaurant_name
        if request.standards:
            context['compliance_standards'] = request.standards
        
        # Process through executor
        result = executor.run(request.query, context=context)
        
        if result['success']:
            # Count menu items analyzed
            menu_items_count = 0
            if 'scratchpad' in result:
                for note in result['scratchpad']:
                    if 'Retrieved' in note and 'items' in note:
                        import re
                        match = re.search(r'(\d+)\s+items', note)
                        if match:
                            menu_items_count = int(match.group(1))
                            break
            
            return ComplianceResponse(
                success=True,
                response=result['response'],
                menu_items_analyzed=menu_items_count,
                compliance_issues=None,  # Could be structured in future
                compliance_score=None   # Could calculate score in future
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Compliance query processing failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance query error: {str(e)}"
        )



