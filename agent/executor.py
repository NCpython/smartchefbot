"""
Executor: Orchestrates the Tool, LLM, and Agent
"""

from typing import Dict, Any, Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from agent.agent import Agent
from tool.menu_tool import MenuTool, menu_tool
from llm.llm_interface import get_llm
from config.settings import MAX_ITERATIONS


class AgentExecutor:
    """
    The Executor provides:
    1. The Tool (menu management)
    2. The LLM (language model)
    3. Calls to the Agent
    
    It orchestrates the entire system and manages the interaction between components.
    """
    
    def __init__(self, max_iterations: int = MAX_ITERATIONS):
        """
        Initialize the executor.
        
        Args:
            max_iterations: Maximum iterations per query
        """
        self.agent = Agent(max_iterations=max_iterations)
        self.tool = menu_tool
        self.llm = None  # Lazy loaded
        self.max_iterations = max_iterations
        
        print(f"Executor initialized with max {max_iterations} iterations")
    
    def _get_llm(self):
        """Lazy load the LLM."""
        if self.llm is None:
            self.llm = get_llm()
        return self.llm
    
    def run(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a user query through the complete system.
        
        This is the main entry point for processing queries.
        
        Args:
            user_query: The user's question or request
            context: Optional additional context
            
        Returns:
            Dictionary containing response and metadata
        """
        print(f"\n{'='*60}")
        print(f"Executing query: {user_query}")
        print(f"{'='*60}\n")
        
        try:
            # Process the query through the agent
            response = self.agent.process_query(user_query, context)
            
            # Prepare result
            result = {
                'success': True,
                'response': response,
                'iterations_used': self.agent.current_iteration,
                'scratchpad': self.agent.scratchpad,
                'max_iterations': self.max_iterations
            }
            
            return result
            
        except Exception as e:
            print(f"Error during execution: {e}")
            return {
                'success': False,
                'response': f"An error occurred: {str(e)}",
                'error': str(e)
            }
    
    def upload_menu(self, pdf_path: str, restaurant_name: str) -> Dict[str, Any]:
        """
        Upload and process a restaurant menu PDF.
        
        This uses the Tool to upload the PDF and the LLM to extract structured data.
        
        Args:
            pdf_path: Path to the PDF file
            restaurant_name: Name of the restaurant
            
        Returns:
            Dictionary containing upload result
        """
        print(f"\n{'='*60}")
        print(f"Uploading menu for: {restaurant_name}")
        print(f"PDF path: {pdf_path}")
        print(f"{'='*60}\n")
        
        try:
            # Use the agent to handle menu upload and extraction
            result_message = self.agent.upload_and_extract_menu(pdf_path, restaurant_name)
            
            return {
                'success': 'Successfully' in result_message,
                'message': result_message,
                'restaurant_name': restaurant_name
            }
            
        except Exception as e:
            print(f"Error uploading menu: {e}")
            return {
                'success': False,
                'message': f"Error uploading menu: {str(e)}",
                'error': str(e)
            }
    
    def list_available_menus(self) -> Dict[str, Any]:
        """
        List all available restaurant menus.
        
        Returns:
            Dictionary containing list of menus
        """
        try:
            menus = self.tool.list_all_menus()
            
            return {
                'success': True,
                'menus': menus,
                'count': len(menus)
            }
            
        except Exception as e:
            return {
                'success': False,
                'menus': [],
                'error': str(e)
            }
    
    def get_menu_items(self, restaurant_name: str) -> Dict[str, Any]:
        """
        Get all menu items for a specific restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            
        Returns:
            Dictionary containing menu items
        """
        try:
            items = self.tool.get_all_menu_items(restaurant_name)
            
            return {
                'success': True,
                'restaurant': restaurant_name,
                'items': items,
                'count': len(items)
            }
            
        except Exception as e:
            return {
                'success': False,
                'items': [],
                'error': str(e)
            }
    
    def search_menus(self, query: str, restaurant_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for menu items across all or specific restaurant.
        
        Args:
            query: Search query
            restaurant_name: Optional specific restaurant to search
            
        Returns:
            Dictionary containing search results
        """
        try:
            if restaurant_name:
                results = self.tool.search_menu_items(restaurant_name, query)
            else:
                # Search all restaurants
                all_menus = self.tool.list_all_menus()
                results = []
                for menu in all_menus:
                    items = self.tool.search_menu_items(menu, query)
                    for item in items:
                        item['restaurant'] = menu
                        results.append(item)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'results': [],
                'error': str(e)
            }


# Create singleton executor instance
executor = AgentExecutor()









