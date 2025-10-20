"""
Agent: The decision-making component that orchestrates LLM and Tools
"""

from typing import Dict, Any, Optional, List
import re
import logging

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import MAX_ITERATIONS, VERBOSE
from agent.prompt import PromptBuilder
from llm.llm_interface import get_llm
from tool.menu_tool import menu_tool

# Create logger
logger = logging.getLogger(__name__)


class Agent:
    """
    The Agent orchestrates decision-making and determines whether to:
    1. Use tools to retrieve menu data
    2. Call the LLM for general queries
    3. Combine both for comprehensive responses
    
    The Agent uses:
    - LLM: For language understanding and generation
    - Tool: For accessing menu data
    - Prompt: For structuring queries appropriately
    """
    
    def __init__(self, max_iterations: int = MAX_ITERATIONS):
        """
        Initialize the Agent.
        
        Args:
            max_iterations: Maximum number of iterations per query
        """
        self.max_iterations = max_iterations
        self.prompt_builder = PromptBuilder()
        self.llm = None  # Lazy loading
        self.current_iteration = 0
        self.scratchpad = []  # Stores thinking process
        
        if VERBOSE:
            logger.info(f"🤖 Agent initialized with max {max_iterations} iterations")
    
    def _get_llm(self):
        """Lazy load LLM to avoid loading it until needed."""
        if self.llm is None:
            self.llm = get_llm()
        return self.llm
    
    def reset(self):
        """Reset the agent state for a new query."""
        self.current_iteration = 0
        self.scratchpad = []
    
    def _add_to_scratchpad(self, thought: str):
        """
        Add a thought to the AI scratchpad.
        
        Args:
            thought: A thought or decision to record
        """
        self.scratchpad.append(f"Iteration {self.current_iteration + 1}: {thought}")
    
    def _get_scratchpad_text(self) -> str:
        """
        Get the current scratchpad as formatted text.
        
        Returns:
            Formatted scratchpad content
        """
        return "\n".join(self.scratchpad)
    
    def _decide_action(self, user_query: str) -> Dict[str, Any]:
        """
        Decide what action to take based on the user query.
        
        Returns:
            Dictionary with action type and parameters
        """
        query_lower = user_query.lower()
        
        if VERBOSE:
            logger.debug(f"🧠 Agent analyzing query: '{user_query[:50]}...'")
        
        # Rule-based decision making (can be enhanced with LLM later)
        
        # Check if query is about uploading or PDF extraction (PRIORITY - check first)
        upload_keywords = ['upload', 'add menu', 'extract menu', 'process pdf', 'analyze pdf']
        if any(keyword in query_lower for keyword in upload_keywords):
            if VERBOSE:
                logger.info("📤 Decision: LLM MODE (pdf_extraction)")
                logger.info("   → Will use LLM (Gemini) for direct PDF processing")
            return {
                'action': 'pdf_extraction',
                'query': user_query
            }
        
        # Check for business/operational queries that need menu data + reasoning
        business_keywords = ['discount', 'expir', 'sale', 'promote', 'special', 'suggest', 'recommend',
                            'should i', 'what should', 'which items', 'inventory', 'stock', 'waste',
                            'profit', 'popular', 'best seller', 'slow moving']
        menu_references = ['menu', 'item', 'dish', 'food', 'ingredient']
        
        if any(biz in query_lower for biz in business_keywords) and any(menu in query_lower for menu in menu_references):
            # This is a business operations query - needs both Tool (menu data) and LLM (business advice)
            if VERBOSE:
                logger.info("💼 Decision: HYBRID MODE (business_operations)")
                logger.info("   → Will use Tool (menu data) + LLM (business advice)")
            return {
                'action': 'business_operations',
                'query': user_query
            }
        
        # Check if query is about menu compliance/recommendations
        compliance_keywords = ['compliant', 'compliance', 'change menu', 'make menu', 'improve menu', 
                             'haccp', 'food safety', 'regulation', 'requirement', 'safe', 'hygiene']
        
        if any(comp in query_lower for comp in compliance_keywords) and any(menu in query_lower for menu in menu_references):
            # This is a menu compliance analysis query - needs both Tool (menu data) and LLM (compliance knowledge)
            if VERBOSE:
                logger.info("🎯 Decision: HYBRID MODE (analyze_menu_compliance)")
                logger.info("   → Will use Tool (menu data) + LLM (compliance knowledge)")
            return {
                'action': 'analyze_menu_compliance',
                'query': user_query
            }
        
        # Check if query mentions specific ingredients/products + menu
        ingredient_keywords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'vegetables', 'dairy', 
                              'eggs', 'rice', 'pasta', 'cheese', 'tomato']
        if any(ing in query_lower for ing in ingredient_keywords) and any(menu in query_lower for menu in menu_references):
            # Ingredient-specific query - use hybrid mode
            if VERBOSE:
                logger.info("🍗 Decision: HYBRID MODE (ingredient_based_query)")
                logger.info("   → Will search menu for ingredients + provide advice")
            return {
                'action': 'business_operations',  # Use same handler as business operations
                'query': user_query
            }
        
        # Check if query is about specific menu items (simple lookup)
        menu_keywords = ['menu', 'item', 'dish', 'food', 'price', 'what do you serve']
        if any(keyword in query_lower for keyword in menu_keywords):
            # Extract restaurant name if mentioned
            # For now, we'll search all available menus
            if VERBOSE:
                logger.info("🔍 Decision: TOOL MODE (search_menu)")
                logger.info("   → Will search menu database")
            return {
                'action': 'search_menu',
                'query': user_query
            }
        
        # Check if query is about listing restaurants/menus
        if 'list' in query_lower and ('restaurant' in query_lower or 'menu' in query_lower):
            if VERBOSE:
                logger.info("📋 Decision: LIST MODE")
            return {
                'action': 'list_menus',
                'query': user_query
            }
        
        # Default: general query to LLM
        if VERBOSE:
            logger.info("🧠 Decision: LLM MODE (general_query)")
            logger.info("   → Will use LLM for general knowledge")
        return {
            'action': 'general_query',
            'query': user_query
        }
    
    def _execute_tool_action(self, action: Dict[str, Any]) -> str:
        """
        Execute a tool-based action.
        
        Args:
            action: Action dictionary from decision
            
        Returns:
            Result from tool execution
        """
        action_type = action['action']
        
        if action_type == 'search_menu':
            # Search across all restaurants (no restaurant_name required!)
            all_results = menu_tool.search_all_restaurants(action['query'])
            
            if not all_results:
                all_menus = menu_tool.list_all_menus()
                if not all_menus:
                    return "No menus available. Please upload a menu first."
                else:
                    return f"No menu items found matching your query. Available restaurants: {', '.join(all_menus)}"
            
            # Format results
            result_text = f"Found {len(all_results)} menu items:\n\n"
            for item in all_results:
                result_text += f"Restaurant: {item.get('restaurant', 'Unknown')}\n"
                result_text += f"Item: {item.get('name', 'Unknown')}\n"
                if 'price' in item:
                    result_text += f"Price: {item['price']}\n"
                if 'description' in item:
                    result_text += f"Description: {item['description']}\n"
                result_text += "\n"
            return result_text
        
        elif action_type == 'list_menus':
            menus = menu_tool.list_all_menus()
            if menus:
                return f"Available restaurant menus: {', '.join(menus)}"
            else:
                return "No menus available yet. Please upload a menu first."
        
        elif action_type == 'upload_menu':
            return "To upload a menu, please use the upload_menu() function with the PDF file path and restaurant name."
        
        return "Unknown action"
    
    def _get_menu_data_for_analysis(self, restaurant_name: str = None) -> Dict[str, Any]:
        """
        Get menu data for compliance analysis.
        
        Args:
            restaurant_name: Optional specific restaurant, otherwise gets all
            
        Returns:
            Dictionary with menu data
        """
        if restaurant_name:
            items = menu_tool.get_all_menu_items(restaurant_name)
            return {
                'restaurant': restaurant_name,
                'items': items,
                'count': len(items)
            }
        else:
            # Get all menus
            all_menus = menu_tool.list_all_menus()
            all_data = {}
            for menu in all_menus:
                items = menu_tool.get_all_menu_items(menu)
                all_data[menu] = {
                    'items': items,
                    'count': len(items)
                }
            return all_data
    
    def _format_menu_for_analysis(self, menu_data: Dict[str, Any]) -> str:
        """
        Format menu data for compliance analysis.
        
        Args:
            menu_data: Menu data from tool
            
        Returns:
            Formatted string with menu items
        """
        if not menu_data:
            return "No menu data available"
        
        formatted = "CURRENT MENU ITEMS:\n\n"
        
        # Check if single restaurant or multiple
        if 'items' in menu_data:
            # Single restaurant
            formatted += f"Restaurant: {menu_data.get('restaurant', 'Unknown')}\n"
            formatted += f"Total items: {menu_data.get('count', 0)}\n\n"
            
            for item in menu_data['items']:
                formatted += f"- {item.get('name', 'Unknown')}"
                if 'price' in item:
                    formatted += f" ({item['price']})"
                if 'description' in item:
                    formatted += f": {item['description']}"
                formatted += "\n"
        else:
            # Multiple restaurants
            for restaurant, data in menu_data.items():
                formatted += f"\nRestaurant: {restaurant}\n"
                formatted += f"Total items: {data.get('count', 0)}\n"
                
                for item in data.get('items', []):
                    formatted += f"- {item.get('name', 'Unknown')}"
                    if 'price' in item:
                        formatted += f" ({item['price']})"
                    if 'description' in item:
                        formatted += f": {item['description']}"
                    formatted += "\n"
                formatted += "\n"
        
        return formatted
    
    def process_query(self, user_query: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user query through the agent pipeline.
        
        Args:
            user_query: The user's question or request
            context: Additional context information
            
        Returns:
            The agent's response
        """
        self.reset()
        
        while self.current_iteration < self.max_iterations:
            self._add_to_scratchpad(f"Processing query: {user_query}")
            
            # Step 1: Decide on action
            action = self._decide_action(user_query)
            self._add_to_scratchpad(f"Decided action: {action['action']}")
            
            # Step 2: Execute action
            if action['action'] == 'business_operations':
                # HYBRID MODE: Combine Tool (menu data) + LLM (business advice)
                self._add_to_scratchpad("Hybrid mode: Business operations with menu data")
                
                if VERBOSE:
                    logger.info("=" * 60)
                    logger.info("💼 HYBRID MODE ACTIVATED - Business Operations")
                    logger.info("=" * 60)
                
                # Get menu data from Tool
                if VERBOSE:
                    logger.info("📥 Step 1: Retrieving menu data from Tool...")
                menu_data = self._get_menu_data_for_analysis()
                
                if not menu_data or (isinstance(menu_data, dict) and not menu_data):
                    if VERBOSE:
                        logger.warning("⚠️  No menu data found in Tool")
                    return "No menu data available. Please upload a menu first so I can help with your business operations."
                
                self._add_to_scratchpad("Retrieved menu data from Tool")
                if VERBOSE:
                    if isinstance(menu_data, dict) and 'items' in menu_data:
                        logger.info(f"✓ Retrieved {len(menu_data['items'])} menu items from Tool")
                    else:
                        total_items = sum(data.get('count', 0) for data in menu_data.values())
                        logger.info(f"✓ Retrieved {total_items} items from {len(menu_data)} restaurants")
                
                # Build context with menu items
                if VERBOSE:
                    logger.info("📝 Step 2: Formatting menu data for LLM...")
                menu_context = self._format_menu_for_analysis(menu_data)
                self._add_to_scratchpad("Formatted menu data for analysis")
                if VERBOSE:
                    logger.info(f"✓ Formatted menu context ({len(menu_context)} characters)")
                
                # Use LLM with menu context to provide business advice
                if VERBOSE:
                    logger.info("🧠 Step 3: Sending to LLM for business analysis...")
                
                business_prompt = f"""You are a smart restaurant business advisor. A restaurant owner has asked you the following question:

"{user_query}"

Here is their current menu data:

{menu_context}

Based on this menu and their question, provide practical, actionable business advice. Be specific about which menu items they should consider and why. Focus on helping them maximize profit, reduce waste, and make smart business decisions.

IMPORTANT FORMATTING REQUIREMENTS:
- Use numbered lists (1., 2., 3.) instead of bullet points or asterisks
- Use proper HTML formatting with <h2>, <h3>, <strong> tags
- Structure your response with clear sections
- Use <div class="highlight-box"> for important recommendations
- Make it visually appealing and easy to scan

Your response should be:
1. Practical and actionable
2. Specific to their actual menu items
3. Clear and easy to understand
4. Focused on business value
5. Well-formatted with proper HTML structure

Respond in a friendly, professional tone with excellent formatting."""
                
                if VERBOSE:
                    logger.info(f"✓ Built business analysis prompt ({len(business_prompt)} characters)")
                    logger.info("💭 LLM is analyzing menu for business recommendations...")
                
                llm = self._get_llm()
                response = llm.generate_response(business_prompt, max_tokens=600)
                
                self._add_to_scratchpad("Generated business recommendations")
                if VERBOSE:
                    logger.info(f"✓ LLM generated response ({len(response)} characters)")
                    logger.info("=" * 60)
                    logger.info("✅ HYBRID MODE COMPLETE")
                    logger.info("=" * 60)
                return response
            
            elif action['action'] == 'analyze_menu_compliance':
                # HYBRID MODE: Combine Tool (menu data) + LLM (compliance knowledge)
                self._add_to_scratchpad("Hybrid mode: Analyzing menu for compliance")
                
                if VERBOSE:
                    logger.info("=" * 60)
                    logger.info("🎯 HYBRID MODE ACTIVATED - Compliance Analysis")
                    logger.info("=" * 60)
                
                # Get menu data from Tool
                if VERBOSE:
                    logger.info("📥 Step 1: Retrieving menu data from Tool...")
                menu_data = self._get_menu_data_for_analysis()
                
                if not menu_data or (isinstance(menu_data, dict) and not menu_data):
                    if VERBOSE:
                        logger.warning("⚠️  No menu data found in Tool")
                    return "No menu data available. Please upload a menu first to analyze it for compliance."
                
                self._add_to_scratchpad("Retrieved menu data from Tool")
                if VERBOSE:
                    if isinstance(menu_data, dict) and 'items' in menu_data:
                        logger.info(f"✓ Retrieved {len(menu_data['items'])} menu items from Tool")
                    else:
                        total_items = sum(data.get('count', 0) for data in menu_data.values())
                        logger.info(f"✓ Retrieved {total_items} items from {len(menu_data)} restaurants")
                
                # Build context with menu items
                if VERBOSE:
                    logger.info("📝 Step 2: Formatting menu data for LLM...")
                menu_context = self._format_menu_for_analysis(menu_data)
                self._add_to_scratchpad("Formatted menu data for analysis")
                if VERBOSE:
                    logger.info(f"✓ Formatted menu context ({len(menu_context)} characters)")
                
                # Use LLM with menu context to provide compliance recommendations
                if VERBOSE:
                    logger.info("🧠 Step 3: Sending to LLM for compliance analysis...")
                analysis_prompt = self.prompt_builder.build_menu_compliance_analysis_prompt(
                    user_query=user_query,
                    menu_data=menu_context,
                    scratchpad=self._get_scratchpad_text()
                )
                
                if VERBOSE:
                    logger.info(f"✓ Built analysis prompt ({len(analysis_prompt)} characters)")
                    logger.info("💭 LLM is analyzing menu against HACCP standards...")
                
                llm = self._get_llm()
                response = llm.generate_response(analysis_prompt, max_tokens=600)
                
                self._add_to_scratchpad("Generated compliance recommendations")
                if VERBOSE:
                    logger.info(f"✓ LLM generated response ({len(response)} characters)")
                    logger.info("=" * 60)
                    logger.info("✅ HYBRID MODE COMPLETE")
                    logger.info("=" * 60)
                return response
            
            elif action['action'] == 'pdf_extraction':
                # LLM MODE: Direct PDF processing with Gemini
                if VERBOSE:
                    logger.info("=" * 60)
                    logger.info("📤 PDF EXTRACTION MODE ACTIVATED")
                    logger.info("=" * 60)
                    logger.info("🧠 Using Gemini for direct PDF processing...")
                
                self._add_to_scratchpad("Processing PDF with Gemini LLM")
                
                # For now, return instruction - in real implementation, this would process the uploaded PDF
                if VERBOSE:
                    logger.info("✓ PDF extraction mode activated")
                    logger.info("📝 Note: PDF file processing will be handled by upload endpoint")
                    logger.info("=" * 60)
                    logger.info("✅ PDF EXTRACTION MODE COMPLETE")
                    logger.info("=" * 60)
                
                return "PDF extraction mode activated. Please upload your PDF file using the upload button above, and Gemini will process it directly to extract menu items."
            
            elif action['action'] in ['search_menu', 'list_menus', 'upload_menu']:
                # Tool-based action
                tool_result = self._execute_tool_action(action)
                self._add_to_scratchpad(f"Tool result obtained")
                
                # If tool returns meaningful data, format it with LLM
                if tool_result and not tool_result.startswith("No menu") and not tool_result.startswith("To upload"):
                    # Use LLM to format the response nicely
                    formatting_prompt = self.prompt_builder.build_prompt(
                        user_input=f"User asked: {user_query}\n\nData from menu tool:\n{tool_result}\n\nPlease provide a helpful, natural response.",
                        ai_scratchpad=self._get_scratchpad_text()
                    )
                    
                    llm = self._get_llm()
                    response = llm.generate_response(formatting_prompt, max_tokens=300)
                    return response if response else tool_result
                else:
                    return tool_result
            
            else:
                # General query - use LLM directly
                self._add_to_scratchpad("Using LLM for general query")
                
                prompt = self.prompt_builder.build_prompt(
                    user_input=user_query,
                    context=context,
                    ai_scratchpad=self._get_scratchpad_text()
                )
                
                llm = self._get_llm()
                response = llm.generate_response(prompt, max_tokens=400)
                
                return response
            
            self.current_iteration += 1
        
        return "Maximum iterations reached. Please try rephrasing your query."
    
    def upload_and_extract_menu(self, pdf_path: str, restaurant_name: str) -> str:
        """
        Upload a menu PDF and extract its contents using the LLM.
        
        Args:
            pdf_path: Path to the PDF file
            restaurant_name: Name of the restaurant
            
        Returns:
            Success message or error
        """
        self.reset()
        self._add_to_scratchpad(f"Uploading menu for {restaurant_name}")
        
        # Step 1: Upload PDF and extract text
        menu_text = menu_tool.upload_pdf(pdf_path, restaurant_name)
        
        if not menu_text:
            return "Error: Could not extract text from PDF"
        
        self._add_to_scratchpad("Text extracted from PDF")
        
        # Step 2: Use LLM to extract structured menu data
        self._add_to_scratchpad("Using LLM to extract menu items")
        llm = self._get_llm()
        menu_data = llm.extract_menu_from_text(menu_text, restaurant_name)
        
        # Step 3: Save the extracted data
        success = menu_tool.save_menu_data(restaurant_name, menu_data)
        
        if success:
            return f"Successfully uploaded and extracted menu for {restaurant_name}. Found {menu_data['total_items']} items."
        else:
            return "Error: Could not save menu data"


# Create singleton agent instance
agent = Agent()

