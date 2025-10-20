#!/bin/bash

# Setup script for SmartChefBot

echo "================================================"
echo "Setting up SmartChefBot"
echo "================================================"

# Step 1: Create virtual environment
echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv

# Step 2: Activate virtual environment
echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

# Step 3: Upgrade pip
echo ""
echo "Step 3: Upgrading pip..."
pip install --upgrade pip

# Step 4: Install requirements
echo ""
echo "Step 4: Installing requirements..."
echo "This may take a few minutes as it downloads PyTorch and Transformers..."
pip install -r requirements.txt

# Step 5: Create necessary directories
echo ""
echo "Step 5: Creating data directories..."
mkdir -p data/menus
mkdir -p data/extracted

echo ""
echo "================================================"
echo "✓ Setup complete!"
echo "================================================"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the chatbot:"
echo "     python main.py"
echo ""
echo "  3. Or run the demo:"
echo "     python main.py demo"
echo ""
echo "Note: The first run will download the LLM model"
echo "      from Hugging Face (approximately 700MB)."
echo "================================================"



