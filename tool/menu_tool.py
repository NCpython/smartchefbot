"""
Menu Tool: Handles menu data storage, retrieval, and PDF extraction
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
import pdfplumber
import logging

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import MENUS_DIR, EXTRACTED_DATA_DIR, VERBOSE

# Create logger
logger = logging.getLogger(__name__)


class MenuTool:
    """
    Tool for managing restaurant menu data.
    
    This tool provides functionality to:
    1. Upload and store menu PDFs
    2. Extract text from PDFs
    3. Store extracted menu data locally
    4. Search and retrieve menu information
    """
    
    def __init__(self):
        self.menus_dir = MENUS_DIR
        self.extracted_dir = EXTRACTED_DATA_DIR
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        text = ""
        
        try:
            # Try with pdfplumber first (better for formatted PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PyPDF2 also failed: {e}")
                return ""
        
        return text.strip()
    
    def save_menu_data(self, restaurant_name: str, menu_data: Dict[str, Any]) -> bool:
        """
        Save extracted menu data to a JSON file.
        
        Args:
            restaurant_name: Name of the restaurant
            menu_data: Dictionary containing menu information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.extracted_dir / f"{restaurant_name}.json"
            with open(file_path, 'w') as f:
                json.dump(menu_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving menu data: {e}")
            return False
    
    def load_menu_data(self, restaurant_name: str) -> Optional[Dict[str, Any]]:
        """
        Load menu data for a specific restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            
        Returns:
            Dictionary containing menu data or None if not found
        """
        try:
            file_path = self.extracted_dir / f"{restaurant_name}.json"
            if file_path.exists():
                if VERBOSE:
                    logger.debug(f"🛠️  Tool: Loading menu data for '{restaurant_name}'")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if VERBOSE:
                    logger.debug(f"🛠️  Tool: Loaded {data.get('total_items', 0)} items")
                return data
            return None
        except Exception as e:
            logger.error(f"Error loading menu data: {e}")
            return None
    
    def search_menu_items(self, restaurant_name: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for menu items matching a query in a specific restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            query: Search query
            
        Returns:
            List of matching menu items
        """
        menu_data = self.load_menu_data(restaurant_name)
        if not menu_data:
            return []
        
        results = []
        query_lower = query.lower()
        
        # Search in menu items
        if 'items' in menu_data:
            for item in menu_data['items']:
                if isinstance(item, dict):
                    # Search in name and description
                    name = item.get('name', '').lower()
                    description = item.get('description', '').lower()
                    
                    if query_lower in name or query_lower in description:
                        results.append(item)
        
        return results
    
    def search_all_restaurants(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for menu items across ALL restaurants.
        
        This is used when no specific restaurant is specified,
        allowing users to search the entire menu database.
        
        Args:
            query: Search query
            
        Returns:
            List of matching menu items with restaurant information
        """
        all_results = []
        query_lower = query.lower()
        
        if VERBOSE:
            logger.info(f"🔍 Searching across all restaurants for: '{query}'")
        
        # Get all available menus
        restaurants = self.list_all_menus()
        
        if not restaurants:
            if VERBOSE:
                logger.warning("⚠️  No restaurant menus available")
            return []
        
        # Search in each restaurant
        for restaurant_name in restaurants:
            results = self.search_menu_items(restaurant_name, query)
            
            # Add restaurant information to each result
            for item in results:
                item['restaurant'] = restaurant_name
                all_results.append(item)
        
        if VERBOSE:
            logger.info(f"✓ Found {len(all_results)} items across {len(restaurants)} restaurants")
        
        return all_results
    
    def list_all_menus(self) -> List[str]:
        """
        List all available restaurant menus.
        
        Returns:
            List of restaurant names
        """
        menus = []
        for file_path in self.extracted_dir.glob("*.json"):
            menus.append(file_path.stem)
        return menus
    
    def get_all_menu_items(self, restaurant_name: str) -> List[Dict[str, Any]]:
        """
        Get all menu items for a restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            
        Returns:
            List of all menu items
        """
        menu_data = self.load_menu_data(restaurant_name)
        if menu_data and 'items' in menu_data:
            return menu_data['items']
        return []
    
    def upload_pdf(self, pdf_path: str, restaurant_name: str) -> str:
        """
        Upload a PDF menu file and extract its text.
        
        Args:
            pdf_path: Path to the PDF file
            restaurant_name: Name of the restaurant
            
        Returns:
            Extracted text from the PDF
        """
        # Copy PDF to menus directory
        destination = self.menus_dir / f"{restaurant_name}.pdf"
        
        try:
            import shutil
            shutil.copy(pdf_path, destination)
            
            # Extract text
            text = self.extract_text_from_pdf(str(destination))
            
            return text
        except Exception as e:
            print(f"Error uploading PDF: {e}")
            return ""
    
    def upload_menu(self, pdf_path: str, restaurant_name: str) -> Dict[str, Any]:
        """
        Upload and process a menu PDF using Gemini AI.
        
        Args:
            pdf_path: Path to the PDF file
            restaurant_name: Name of the restaurant
            
        Returns:
            Dictionary with extraction results
        """
        try:
            # Import LLM interface
            from llm.llm_interface import get_llm
            
            # Get LLM instance
            llm = get_llm()
            
            # Process PDF with Gemini
            logger.info(f"🧠 Gemini: Processing PDF directly for '{restaurant_name}'")
            result = llm.extract_menu_from_pdf(pdf_path, restaurant_name)
            
            # Save the extracted data
            if result and 'items' in result:
                self.save_menu_data(restaurant_name, result)
                logger.info(f"✓ Gemini extracted {len(result['items'])} menu items from PDF")
                
                return {
                    'success': True,
                    'item_count': len(result['items']),
                    'restaurant_name': restaurant_name,
                    'data': result
                }
            else:
                logger.error("❌ Failed to extract menu items from PDF")
                return {
                    'success': False,
                    'item_count': 0,
                    'restaurant_name': restaurant_name,
                    'error': 'No items extracted'
                }
                
        except Exception as e:
            logger.error(f"Error uploading menu: {e}")
            return {
                'success': False,
                'item_count': 0,
                'restaurant_name': restaurant_name,
                'error': str(e)
            }
    
    def list_menus(self) -> List[Dict[str, Any]]:
        """
        List all uploaded menus with their data.
        
        Returns:
            List of menu dictionaries
        """
        menus = []
        
        try:
            # Iterate through all JSON files in extracted directory
            for file_path in self.extracted_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        menu_data = json.load(f)
                        
                    # Add restaurant name from filename
                    restaurant_name = file_path.stem
                    
                    menus.append({
                        'restaurant_name': restaurant_name,
                        'items': menu_data.get('items', []),
                        'total_items': menu_data.get('total_items', len(menu_data.get('items', [])))
                    })
                    
                except Exception as e:
                    logger.error(f"Error loading menu from {file_path}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error listing menus: {e}")
            
        return menus
    
    def clear_all_data(self) -> bool:
        """
        Clear all menu data (PDFs and JSON files).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear extracted JSON files
            for file_path in self.extracted_dir.glob("*.json"):
                file_path.unlink()
                
            # Clear uploaded PDFs
            for file_path in self.menus_dir.glob("*.pdf"):
                file_path.unlink()
                
            logger.info("✓ All menu data cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False


# Create a singleton instance
menu_tool = MenuTool()

