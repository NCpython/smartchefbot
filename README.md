

# 🍽️ SmartChefBot

A customized language model chatbot that helps restaurant owners with menu management and compliance queries.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-green.svg)](https://github.com)

## ✨ Features

- 💼 **Business Operations Assistant**: Get smart advice on inventory, discounts, promotions, and menu optimization
- 🤖 **Intelligent Agent**: Decides when to use tools vs. LLM for optimal responses
- 📄 **PDF Menu Upload**: Automatically extract menu items from restaurant PDFs using Gemini AI
- 🔍 **Smart Search**: Find menu items across all uploaded restaurants
- ✅ **Compliance Expert**: Get HACCP and food safety recommendations for YOUR specific menu
- 🎯 **Hybrid Mode**: Combines your actual menu data with AI reasoning for personalized advice
- 🧠 **Transparent Thinking**: See the AI's decision-making process
- ⚡ **Efficient**: Limited to 5 iterations per query
- 🔒 **Privacy-First**: All data stored locally

## 🏗️ Architecture

The system implements an **Agent-Tool-LLM** architecture with three main components:

### 1. **Agent** 🤖
Orchestrates decision-making and workflow
- Analyzes user queries
- Decides when to use tools vs. LLM
- Manages iteration control (max 5)
- Tracks thinking process in scratchpad

### 2. **Tool** 🛠️
Manages restaurant menu data
- PDF text extraction
- Local JSON storage
- Menu search functionality
- Data retrieval

### 3. **LLM** 🧠
Hugging Face open-source language model
- Menu item extraction from PDFs
- Natural language understanding
- Compliance question answering
- Response generation

### 4. **Executor** ⚙️
Orchestrates all components
- Provides Tool to Agent
- Provides LLM to Agent
- Manages complete workflow
- Handles errors

## 📊 System Flow

```
User Query
    ↓
┌──────────────┐
│   Executor   │ ← Orchestrates everything
└──────┬───────┘
       ↓
┌──────────────┐
│    Agent     │ ← Decides: Tool or LLM?
└──────┬───────┘
       ↓
    ┌──┴──┐
    ↓     ↓
┌──────┐ ┌─────┐
│ Tool │ │ LLM │ ← Execute action
└──┬───┘ └──┬──┘
   └────┬────┘
        ↓
   Response
```

## 🎯 Prompt Structure

Three-part prompt system for optimal AI behavior:

1. **System Prompt**: Defines AI behavior and available tools
2. **AI Scratchpad**: Where the AI thinks and plans (visible to user)
3. **User Input**: The actual query

## 🚀 Quick Start

### 1. Run Setup Script
```bash
cd /Users/nishantchaturvedi/Desktop/fnb-intelligence
./setup.sh
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Start Chatting
```bash
python main.py
```

**Note**: First run downloads the LLM model (~700MB). Subsequent runs are fast!

## 💬 Usage Examples

### Interactive Mode
```bash
$ python main.py

💬 You: What are food safety requirements for restaurants?
🤖 AI: [Detailed compliance information]

💬 You: upload sample_menu.pdf "My Restaurant"
✓ Successfully uploaded menu! Found 12 items.

💬 You: What vegetarian dishes are available?
🤖 AI: [Lists vegetarian items from uploaded menus]

💬 You: list menus
📋 Available Menus: My Restaurant

💬 You: quit
👋 Goodbye!
```

### Demo Mode
```bash
python main.py demo
```

### Programmatic Usage
```python
from agent import executor

# Ask a compliance question
result = executor.run("What temperature should food be stored at?")
print(result['response'])

# Upload a menu
result = executor.upload_menu("menu.pdf", "Restaurant Name")
print(result['message'])

# Search menus
result = executor.search_menus("pizza")
print(f"Found {result['count']} items")
```

## 📁 Project Structure

```
fnb-intelligence/
├── agent/                      # Agent Component
│   ├── agent.py               # Decision-making logic
│   ├── executor.py            # Orchestrates Tool + LLM + Agent
│   └── prompt.py              # 3-part prompt builder
├── tool/                       # Tool Component
│   └── menu_tool.py           # PDF extraction & data storage
├── llm/                        # LLM Component
│   └── llm_interface.py       # Hugging Face integration
├── config/                     # Configuration
│   └── settings.py            # All settings & prompts
├── data/                       # Local Storage
│   ├── menus/                 # Uploaded PDFs
│   └── extracted/             # Extracted JSON data
├── main.py                     # Main entry point
├── example_usage.py            # Usage examples
├── setup.sh                    # Installation script
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── GETTING_STARTED.md         # Beginner guide
├── ARCHITECTURE.md            # Technical details
└── PROJECT_SUMMARY.md         # Complete summary
```

## 📚 Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [README.md](README.md) | Quick overview and setup | Everyone |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Step-by-step beginner guide | Beginners |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture details | Developers |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Complete project summary | Everyone |
| [COMPLIANCE_ANALYSIS.md](COMPLIANCE_ANALYSIS.md) | Menu compliance analysis feature | Restaurant owners |

## ⚙️ Configuration

All settings in `config/settings.py`:

```python
# LLM Model (changeable)
DEFAULT_LLM_MODEL = "facebook/opt-350m"  # Fast, small
# or "google/flan-t5-base" for better quality

# Iteration Limit
MAX_ITERATIONS = 5  # Prevents infinite loops

# Response Settings
TEMPERATURE = 0.7
MAX_LENGTH = 512
```

## 🎯 Use Cases

### Restaurant Owners
- Upload and manage menus
- Query menu items quickly
- Get compliance information
- Understand food safety regulations

### Compliance Officers
- Quick regulation lookups
- Food safety guidelines
- HACCP requirements
- Temperature requirements

### Developers
- Extend with new tools
- Add custom LLM providers
- Integrate with existing systems
- Build on the architecture

## 🔧 Requirements

- Python 3.8 or higher
- 2GB free disk space (for LLM model)
- Internet connection (first-time setup only)

## 📦 Dependencies

Main packages:
- `transformers` - Hugging Face models
- `torch` - Deep learning
- `PyPDF2` & `pdfplumber` - PDF processing
- `fastapi` - API framework (optional)

See `requirements.txt` for complete list.

## 🎓 Key Concepts

### Agent
The "brain" that decides what action to take based on the query.

### Tool
The "filing cabinet" that stores and retrieves menu data.

### LLM
The "language expert" that understands and generates text.

### Executor
The "manager" that coordinates Agent, Tool, and LLM.

### Scratchpad
The "notepad" where AI writes its thinking process (visible to users).

### Iteration Limit
Maximum 5 loops to prevent infinite processing.

## 🌟 Advanced Features

### AI Scratchpad Visibility
See how the AI thinks:
```
Iteration 1: Processing query: What vegetarian options?
Iteration 2: Decided action: search_menu
Iteration 3: Tool result obtained
```

### Triple-Mode Operation
- **Tool Mode**: Queries menu data
- **LLM Mode**: General compliance and business questions
- **🎯 Hybrid Mode**: Combines menu data + AI reasoning for specific recommendations
  - **Business Operations**: "My chicken is expiring today, what items should I discount?"
  - **Compliance Analysis**: "How can I make my menu HACCP compliant?"
  - **Inventory Management**: "What menu items use chicken as an ingredient?"
  - Analyzes YOUR actual menu items
  - Provides actionable, menu-specific advice

### Customizable Behavior
Edit `config/settings.py` to change:
- System prompt (AI personality)
- Model selection
- Iteration limits
- Response parameters

## 🤝 Contributing

This is a complete, working system ready for customization and extension!

## 📄 License

MIT License - Feel free to use and modify!

## 🎉 Getting Help

1. Read `GETTING_STARTED.md` for detailed setup
2. Check `ARCHITECTURE.md` for technical details
3. Run examples: `python example_usage.py`
4. Try demo: `python main.py demo`

---

**Ready to start?** Run `./setup.sh` and then `python main.py`

Built with ❤️ for restaurant owners and compliance professionals

