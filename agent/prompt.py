"""
Prompt Structure: System, AI Scratchpad, and User Input
"""

from typing import List, Dict, Any
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import SYSTEM_PROMPT, TOOL_DESCRIPTIONS


@dataclass
class PromptComponent:
    """Represents a single component of the prompt"""
    role: str  # 'system', 'ai', 'user'
    content: str


class PromptBuilder:
    """
    Builds prompts with three parts:
    1. System: Defines behavior and diet of the AI
    2. AI Scratchpad: Where AI thinks and decides
    3. User Input: The actual user query
    """
    
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        """
        Initialize the prompt builder.
        
        Args:
            system_prompt: The system-level prompt defining AI behavior
        """
        self.system_prompt = system_prompt
        self.conversation_history: List[PromptComponent] = []
    
    def build_prompt(self, user_input: str, context: Dict[str, Any] = None,
                    ai_scratchpad: str = "") -> str:
        """
        Build a complete prompt with all three components.
        
        Args:
            user_input: The user's query
            context: Additional context (e.g., menu data, previous actions)
            ai_scratchpad: AI's thinking process and decisions
            
        Returns:
            Complete formatted prompt
        """
        prompt_parts = []
        
        # 1. System Component
        prompt_parts.append(f"### SYSTEM ###\n{self.system_prompt}\n")
        
        # Add available tools to system prompt
        prompt_parts.append("\n### AVAILABLE TOOLS ###")
        for tool_name, tool_desc in TOOL_DESCRIPTIONS.items():
            prompt_parts.append(f"- {tool_name}: {tool_desc}")
        
        # 2. Context (if available)
        if context:
            prompt_parts.append("\n### CONTEXT ###")
            for key, value in context.items():
                prompt_parts.append(f"{key}: {value}")
        
        # 3. AI Scratchpad Component
        if ai_scratchpad:
            prompt_parts.append(f"\n### AI SCRATCHPAD ###\n{ai_scratchpad}\n")
        else:
            prompt_parts.append("\n### AI SCRATCHPAD ###")
            prompt_parts.append("Thinking: Let me analyze this query and decide the best approach...")
            prompt_parts.append("Decision: ")
        
        # 4. User Input Component
        prompt_parts.append(f"\n### USER INPUT ###\n{user_input}\n")
        
        # 5. Response section
        prompt_parts.append("\n### ASSISTANT RESPONSE ###")
        
        return "\n".join(prompt_parts)
    
    def build_tool_decision_prompt(self, user_input: str, available_tools: List[str]) -> str:
        """
        Build a prompt to help the agent decide which tool to use.
        
        Args:
            user_input: The user's query
            available_tools: List of available tool names
            
        Returns:
            Prompt for tool decision
        """
        prompt = f"""### SYSTEM ###
You are an AI agent that decides which tool to use for a given query.

### AVAILABLE TOOLS ###
{', '.join(available_tools)}

### TASK ###
Analyze the user's query and decide if you need to use a tool or can answer directly.

If the query is about:
- Specific menu items → use 'menu_search' tool
- Listing menu items → use 'menu_list' tool  
- Uploading a menu → use 'menu_upload' tool
- General compliance/restaurant questions → answer directly (use 'none')

### USER INPUT ###
{user_input}

### AI SCRATCHPAD ###
Thinking: Let me analyze what the user is asking for...
Analysis: 
"""
        return prompt
    
    def build_menu_extraction_prompt(self, menu_text: str) -> str:
        """
        Build a prompt for menu extraction from PDF text.
        
        Args:
            menu_text: Raw text from menu PDF
            
        Returns:
            Prompt for menu extraction
        """
        prompt = f"""### SYSTEM ###
You are an expert at extracting structured menu data from text.
Extract menu items with their names, prices (in Euros), and descriptions.

### USER INPUT ###
Please extract all menu items from this text:

{menu_text[:1500]}

### AI SCRATCHPAD ###
Thinking: I need to identify menu items, their prices, and descriptions from this text.
Approach: I'll look for patterns that indicate menu items (usually have names and prices).

### ASSISTANT RESPONSE ###
Here are the extracted menu items:
"""
        return prompt
    
    def build_menu_compliance_analysis_prompt(self, user_query: str, menu_data: str, 
                                             scratchpad: str = "") -> str:
        """
        Build a prompt for analyzing menu compliance with regulations.
        
        This is a HYBRID prompt that combines:
        - Menu data from the Tool
        - Compliance knowledge from the LLM
        
        Args:
            user_query: The user's compliance question
            menu_data: Formatted menu data from the tool
            scratchpad: AI's thinking process
            
        Returns:
            Prompt for menu compliance analysis
        """
        prompt = f"""### SYSTEM ###
You are an expert restaurant compliance consultant specializing in HACCP (Hazard Analysis and Critical Control Points) and food safety regulations.

Your task is to analyze restaurant menus and provide specific, actionable recommendations to ensure compliance with food safety standards.

IMPORTANT FORMATTING REQUIREMENTS:
- Use numbered lists (1., 2., 3.) instead of bullet points or asterisks
- Use proper HTML formatting with <h2>, <h3>, <strong> tags
- Structure your response with clear sections
- Use <div class="highlight-box"> for critical recommendations
- Make it visually appealing and easy to scan

### AVAILABLE TOOLS ###
- menu_data: Access to current restaurant menu items

### CONTEXT - CURRENT MENU DATA ###
{menu_data}

### AI SCRATCHPAD ###
{scratchpad if scratchpad else 'Thinking: I will analyze the menu items against HACCP and food safety requirements...'}

Step 1: Review the current menu items
Step 2: Identify potential compliance issues
Step 3: Provide specific recommendations for each issue
Step 4: Suggest menu modifications or additions

### USER INPUT ###
{user_query}

### ASSISTANT RESPONSE ###
<div class="highlight-box">
<h2>🍽️ HACCP Compliance Analysis</h2>
<p>Based on my analysis of your current menu and HACCP requirements, here are my recommendations:</p>
</div>

<h2>1. Current Menu Review</h2>
"""
        return prompt
    
    def add_to_history(self, role: str, content: str):
        """
        Add a prompt component to conversation history.
        
        Args:
            role: Role ('system', 'ai', 'user')
            content: Content of the message
        """
        self.conversation_history.append(PromptComponent(role=role, content=content))
    
    def get_conversation_context(self) -> str:
        """
        Get the conversation history as context.
        
        Returns:
            Formatted conversation history
        """
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for component in self.conversation_history[-5:]:  # Last 5 exchanges
            context_parts.append(f"{component.role.upper()}: {component.content}")
        
        return "\n".join(context_parts)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# Create a default prompt builder instance
default_prompt_builder = PromptBuilder()

