"""
LLM Interface: Handles interaction with Google Gemini AI
"""

from typing import Dict, Any, Optional
import json
import re
import logging
import google.generativeai as genai

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_TOKENS, VERBOSE

# Create logger
logger = logging.getLogger(__name__)


class LLMInterface:
    """
    Interface for interacting with Google Gemini AI.
    
    Provides functionality for:
    1. General query answering
    2. Menu extraction from text
    3. Text generation with context
    """
    
    def __init__(self, api_key: str = GEMINI_API_KEY, model_name: str = GEMINI_MODEL):
        """
        Initialize the Gemini LLM interface.
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use
        """
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not set! Please add your API key to the .env file. "
                "Get your key from: https://makersuite.google.com/app/apikey"
            )
        
        self.model_name = model_name
        
        if VERBOSE:
            logger.info(f"🚀 Initializing Gemini AI: {model_name}")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(model_name)
        
        if VERBOSE:
            logger.info("✓ Gemini AI initialized successfully!")
        
        print(f"✓ Gemini AI ({model_name}) ready!")
    
    def generate_response(self, prompt: str, max_tokens: int = MAX_TOKENS, 
                         temperature: float = TEMPERATURE) -> str:
        """
        Generate a response from Gemini AI.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum number of tokens in response
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        try:
            if VERBOSE:
                logger.debug(f"🧠 Gemini: Generating response (max_tokens={max_tokens}, temp={temperature})")
                logger.debug(f"🧠 Gemini: Prompt length: {len(prompt)} characters")
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text from response
            if response.text:
                result = response.text.strip()
                
                if VERBOSE:
                    logger.debug(f"🧠 Gemini: Generated {len(result)} characters")
                
                return result
            else:
                logger.warning("⚠️  Gemini returned empty response")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return f"Error generating response: {str(e)}"
    
    def extract_menu_from_text(self, text: str, restaurant_name: str) -> Dict[str, Any]:
        """
        Extract structured menu data from raw text using Gemini AI.
        
        This uses Gemini to parse menu text and extract items with details.
        
        Args:
            text: Raw text extracted from PDF
            restaurant_name: Name of the restaurant
            
        Returns:
            Dictionary containing structured menu data
        """
        if VERBOSE:
            logger.info(f"🧠 Gemini: Extracting menu items for '{restaurant_name}'")
        
        # Create a prompt for menu extraction
        extraction_prompt = f"""Extract menu items from the following restaurant menu text.
For each item, identify the name, price (in Euros), and description if available.

Menu Text:
{text[:3000]}

Please list the menu items in the following format:
Item: [name] | Price: [price] | Description: [description]

Only extract actual menu items with prices. Ignore headers, footers, and non-food items.

Menu Items:"""
        
        # Generate extraction
        response = self.generate_response(extraction_prompt, max_tokens=2048)
        
        # Parse the response to extract structured data
        menu_items = self._parse_menu_response(response, text)
        
        if VERBOSE:
            logger.info(f"✓ Gemini extracted {len(menu_items)} menu items")
        
        menu_data = {
            "restaurant_name": restaurant_name,
            "raw_text": text,
            "items": menu_items,
            "total_items": len(menu_items)
        }
        
        return menu_data
    
    def _parse_menu_response(self, response: str, original_text: str) -> list:
        """
        Parse the LLM response to extract menu items.
        
        Args:
            response: LLM generated response
            original_text: Original menu text
            
        Returns:
            List of menu items
        """
        items = []
        
        try:
            # First, try to extract JSON from markdown code blocks
            if '```json' in response:
                # Extract JSON from markdown
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                if json_end > json_start:
                    json_text = response[json_start:json_end].strip()
                    if VERBOSE:
                        logger.debug(f"📄 Extracted JSON from markdown: {json_text[:200]}...")
                    
                    # Parse the JSON
                    import json
                    parsed_items = json.loads(json_text)
                    if isinstance(parsed_items, list):
                        items = parsed_items
                        if VERBOSE:
                            logger.debug(f"✓ Successfully parsed {len(items)} items from JSON")
                        return items
            
            # Try to parse as direct JSON
            import json
            parsed_items = json.loads(response.strip())
            if isinstance(parsed_items, list):
                items = parsed_items
                if VERBOSE:
                    logger.debug(f"✓ Successfully parsed {len(items)} items from direct JSON")
                return items
                
        except json.JSONDecodeError as e:
            if VERBOSE:
                logger.debug(f"❌ JSON parsing failed: {e}")
        
        # Fallback: Try to parse structured format
        lines = response.split('\n')
        
        for line in lines:
            if '|' in line and ('Item:' in line or 'Price:' in line):
                # Parse structured format
                item_data = {}
                parts = line.split('|')
                
                for part in parts:
                    part = part.strip()
                    if part.startswith('Item:'):
                        item_data['name'] = part.replace('Item:', '').strip()
                    elif part.startswith('Price:'):
                        price_str = part.replace('Price:', '').strip()
                        # Extract Euro amount
                        price_match = re.search(r'€?\s*(\d+(?:\.\d{2})?)', price_str)
                        if price_match:
                            item_data['price'] = f"€{price_match.group(1)}"
                    elif part.startswith('Description:'):
                        item_data['description'] = part.replace('Description:', '').strip()
                
                if 'name' in item_data:
                    items.append(item_data)
        
        # If structured parsing didn't work, do simple extraction from original text
        if len(items) == 0:
            items = self._simple_menu_extraction(original_text)
        
        return items
    
    def _simple_menu_extraction(self, text: str) -> list:
        """
        Simple rule-based menu extraction as fallback.
        
        Args:
            text: Menu text
            
        Returns:
            List of extracted menu items
        """
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for price patterns (€XX.XX or €XX)
            price_match = re.search(r'€\s*(\d+(?:\.\d{2})?)', line)
            
            if price_match:
                price = f"€{price_match.group(1)}"
                # Everything before the price is likely the item name
                name = line[:price_match.start()].strip()
                # Everything after might be description
                description = line[price_match.end():].strip()
                
                if name:
                    item = {
                        'name': name,
                        'price': price
                    }
                    if description:
                        item['description'] = description
                    items.append(item)
        
        return items
    
    def extract_menu_from_pdf(self, pdf_path: str, restaurant_name: str) -> Dict[str, Any]:
        """
        Extract menu items from PDF using ONLY Gemini 2.0 Flash.
        
        Args:
            pdf_path: Path to the PDF file
            restaurant_name: Name of the restaurant
            
        Returns:
            Dictionary with extracted menu data
        """
        try:
            if VERBOSE:
                logger.info(f"🧠 Gemini: Processing PDF directly for '{restaurant_name}'")
            
            # Use Gemini 2.5 Flash for direct PDF processing (better multimodal support)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Read PDF file and encode as base64
            import base64
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = base64.b64encode(pdf_file.read()).decode()
            
            if VERBOSE:
                logger.debug(f"📄 PDF encoded: {len(pdf_data)} characters")
            
            # Create detailed prompt for PDF analysis
            pdf_prompt = f"""
            You are a menu extraction expert. Analyze this restaurant menu PDF and extract ALL menu items.
            
            Restaurant: {restaurant_name}
            
            Instructions:
            1. Look through the ENTIRE PDF carefully
            2. Extract EVERY menu item you can find
            3. Include names, prices, and descriptions
            4. Group items by categories if visible
            5. Return ONLY a JSON array of items
            
            Required JSON format:
            [
                {{
                    "name": "Exact item name",
                    "price": "Price with currency symbol",
                    "description": "Item description if available",
                    "category": "Category name if visible"
                }}
            ]
            
            Be extremely thorough and extract ALL menu items from every page.
            """
            
            if VERBOSE:
                logger.debug(f"🧠 Sending PDF to Gemini for analysis")
            
            # Send PDF to Gemini with the prompt
            response = model.generate_content([
                pdf_prompt,
                {
                    "mime_type": "application/pdf",
                    "data": pdf_data
                }
            ])
            
            if response.text:
                if VERBOSE:
                    logger.debug(f"🧠 Gemini raw response: {response.text[:500]}...")
                
                # Parse the JSON response from Gemini
                menu_data = self._parse_menu_response(response.text, "PDF extraction")
                
                if VERBOSE:
                    logger.info(f"✓ Gemini extracted {len(menu_data)} menu items from PDF")
                    if menu_data:
                        logger.debug(f"Sample items: {menu_data[:2]}")
                
                result = {
                    "restaurant_name": restaurant_name,
                    "items": menu_data,
                    "total_items": len(menu_data),
                    "extraction_method": "gemini_direct_pdf",
                    "pdf_path": pdf_path,
                    "raw_gemini_response": response.text[:1000] + "..." if len(response.text) > 1000 else response.text
                }
                
                return result
            else:
                logger.error("❌ Gemini returned empty response")
                return {
                    "restaurant_name": restaurant_name,
                    "items": [],
                    "total_items": 0,
                    "extraction_method": "gemini_direct_pdf",
                    "error": "Empty response from Gemini"
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing PDF with Gemini: {e}")
            return {
                "restaurant_name": restaurant_name,
                "items": [],
                "total_items": 0,
                "extraction_method": "gemini_direct_pdf",
                "error": str(e)
            }


# Singleton instance - will be initialized on first use
_llm_instance = None


def get_llm() -> LLMInterface:
    """
    Get the LLM interface singleton instance.
    
    Returns:
        LLMInterface instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMInterface()
    return _llm_instance

