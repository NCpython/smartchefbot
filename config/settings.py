"""
Configuration settings for SmartChefBot
"""

import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging Configuration
VERBOSE = True  # Set to True to see detailed logs
LOG_LEVEL = logging.DEBUG if VERBOSE else logging.INFO

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
MENUS_DIR = DATA_DIR / "menus"
EXTRACTED_DATA_DIR = DATA_DIR / "extracted"

# Create directories if they don't exist
MENUS_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Google Gemini Configuration
# Support both GOOGLE_API_KEY and GEMINI_API_KEY for compatibility
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Gemini Flash 2.0 - Fast and efficient

# Validate API key
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("⚠️  WARNING: GOOGLE_API_KEY not set in environment variables!")
    print("Please add your Gemini API key to Railway environment variables")
    print("Get your key from: https://makersuite.google.com/app/apikey")

# Agent Configuration
MAX_ITERATIONS = 5  # Maximum number of iterations per query
TEMPERATURE = 0.7
MAX_TOKENS = 1024  # Maximum response tokens

# System Prompt
SYSTEM_PROMPT = """You are SmartChefBot, a helpful AI assistant specialized in restaurant operations, business advice, and compliance.

Your role is to help restaurant owners with:
- 💼 Business Operations: inventory management, discounts, promotions, menu optimization
- 🍽️ Menu Management: menu items, ingredients, pricing, item recommendations
- ✅ Food Safety & Compliance: HACCP, regulations, health and safety guidelines
- 📊 Business Intelligence: profit optimization, waste reduction, popular items analysis
- 🎯 Practical Advice: day-to-day operational questions and decision-making

You have access to the restaurant's actual menu data and can provide specific, actionable advice based on their real menu items.

When helping with business decisions:
- Be specific about which menu items to consider
- Provide practical, actionable recommendations
- Focus on maximizing profit and reducing waste
- Consider ingredient overlap and inventory management

Always be professional, accurate, and helpful. Provide advice that restaurant owners can immediately act upon."""

# Tool descriptions
TOOL_DESCRIPTIONS = {
    "menu_search": "Search for menu items and their details from uploaded restaurant menus",
    "menu_list": "List all available menu items for a restaurant",
    "menu_upload": "Upload and extract menu data from a PDF file"
}

