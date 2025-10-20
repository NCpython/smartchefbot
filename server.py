"""
Web Server for SmartChefBot
Runs on port 3000 with a web interface
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Lazy imports - don't import heavy modules at startup
# These will be imported only when needed
executor = None
menu_tool = None

def get_executor():
    """Lazy load executor only when needed"""
    global executor
    if executor is None:
        from agent import executor as _executor
        executor = _executor
    return executor

def get_menu_tool():
    """Lazy load menu_tool only when needed"""
    global menu_tool
    if menu_tool is None:
        from tool import menu_tool as _menu_tool
        menu_tool = _menu_tool
    return menu_tool

# Import new API routers
from api.v1 import menus, query, items, system

# Create FastAPI app
app = FastAPI(
    title="SmartChefBot",
    description="AI-powered chatbot for restaurant menu analysis and compliance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include API routers (new structured API endpoints)
app.include_router(menus.router)
app.include_router(query.router)
app.include_router(items.router)
app.include_router(system.router)


# Request/Response Models (keeping for backward compatibility with existing endpoints)
class QueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None


class QueryResponse(BaseModel):
    success: bool
    response: str
    iterations_used: Optional[int] = None
    scratchpad: Optional[list] = None
    error: Optional[str] = None


class MenuUploadResponse(BaseModel):
    success: bool
    message: str
    restaurant_name: Optional[str] = None


class MenuListResponse(BaseModel):
    success: bool
    menus: list
    count: int


# Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartChefBot - Enterprise Restaurant Intelligence</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #f8fafc;
                color: #1e293b;
                line-height: 1.6;
            }
            .navbar {
                background: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .navbar-brand {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
            }
            .navbar-nav {
                display: flex;
                gap: 2rem;
                list-style: none;
            }
            .navbar-nav a {
                text-decoration: none;
                color: #64748b;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            .navbar-nav a:hover, .navbar-nav a.active {
                color: #1e293b;
                background: #f1f5f9;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 4rem 2rem;
            }
            .hero {
                text-align: center;
                margin-bottom: 4rem;
            }
            .hero h1 {
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1.5rem;
                color: #0f172a;
                line-height: 1.1;
            }
            .hero p {
                font-size: 1.25rem;
                margin-bottom: 2.5rem;
                color: #64748b;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                margin-bottom: 4rem;
            }
            .feature-card {
                background: #ffffff;
                padding: 2rem;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                transition: all 0.2s ease;
            }
            .feature-card:hover {
                border-color: #cbd5e1;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            .feature-card h3 {
                color: #0f172a;
                margin-bottom: 1rem;
                font-size: 1.25rem;
                font-weight: 600;
            }
            .feature-card p {
                color: #64748b;
                line-height: 1.6;
            }
            .cta {
                text-align: center;
            }
            .btn {
                display: inline-block;
                padding: 0.875rem 2rem;
                background: #1e293b;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.2s ease;
                border: none;
                cursor: pointer;
                font-size: 1rem;
            }
            .btn:hover {
                background: #334155;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(30, 41, 59, 0.15);
            }
            .btn-secondary {
                background: transparent;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                margin-left: 1rem;
            }
            .btn-secondary:hover {
                background: #f8fafc;
                border-color: #cbd5e1;
            }
            .powered-by {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                font-size: 0.875rem;
                color: #64748b;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            .powered-by .ioms {
                color: #1e293b;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">SmartChefBot</div>
            <ul class="navbar-nav">
                <li><a href="/" class="active">Home</a></li>
                <li><a href="/chat">Chat</a></li>
                <li><a href="/data">Data</a></li>
            </ul>
        </nav>
        
        <div class="container">
            <div class="hero">
                <h1>SmartChefBot</h1>
                <p>AI-powered restaurant operations, menu optimization & compliance assistance</p>
                <div class="cta">
                    <a href="/chat" class="btn">Start Chatting</a>
                    <a href="/data" class="btn btn-secondary">View Data</a>
                </div>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>Business Operations</h3>
                    <p>Get intelligent recommendations for inventory management, pricing strategies, and operational efficiency based on your menu data.</p>
                </div>
                <div class="feature-card">
                    <h3>Compliance Analysis</h3>
                    <p>Ensure your restaurant meets HACCP and food safety regulations with automated compliance checking and recommendations.</p>
                </div>
                <div class="feature-card">
                    <h3>Smart Recommendations</h3>
                    <p>Receive data-driven insights for menu optimization, waste reduction, and profit maximization tailored to your restaurant.</p>
                </div>
            </div>
        </div>
        
        <div class="powered-by">
            Powered by <span class="ioms">IOMS</span>
        </div>
    </body>
    </html>
    """


@app.get("/chat", response_class=HTMLResponse)
async def chat():
    """Serve the chat interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartChefBot - Chat</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #f8fafc;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .navbar {
                background: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem 2rem;
            }
            .navbar-brand {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
            }
            .navbar-links {
                display: flex;
                gap: 2rem;
                list-style: none;
            }
            .navbar-links a {
                text-decoration: none;
                color: #64748b;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            .navbar-links a:hover, .navbar-links a.active {
                color: #1e293b;
                background: #f1f5f9;
            }
            .header {
                background: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                padding: 1rem 2rem;
                text-align: center;
            }
            .header h1 { 
                font-size: 1.5rem; 
                margin-bottom: 0.5rem; 
                color: #0f172a;
                font-weight: 600;
            }
            .header p {
                color: #64748b;
                font-size: 0.875rem;
            }
            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                max-width: 1200px;
                margin: 0 auto;
                width: 100%;
                background: #ffffff;
                border-left: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
            }
            .chat-messages {
                flex: 1;
                padding: 2rem;
                overflow-y: auto;
                background: #f8fafc;
            }
            .message {
                margin-bottom: 1.5rem;
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
            }
            .message.user {
                flex-direction: row-reverse;
            }
            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.875rem;
                font-weight: 600;
                flex-shrink: 0;
            }
            .message.bot .message-avatar {
                background: #1e293b;
                color: white;
            }
            .message.user .message-avatar {
                background: #3b82f6;
                color: white;
            }
            .message-content {
                max-width: 70%;
                padding: 1rem 1.25rem;
                border-radius: 12px;
                font-size: 0.875rem;
                line-height: 1.5;
            }
            .message.bot .message-content {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                color: #1e293b;
            }
            .message.user .message-content {
                background: #3b82f6;
                color: white;
            }
            .message-content h1, .message-content h2, .message-content h3 {
                color: #0f172a;
                margin: 1rem 0 0.5rem 0;
                font-weight: 600;
            }
            .message-content h1 {
                font-size: 1.125rem;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 0.5rem;
            }
            .message-content h2 {
                font-size: 1rem;
                color: #1e293b;
            }
            .message-content h3 {
                font-size: 0.875rem;
                color: #475569;
            }
            .message-content ul {
                margin: 0.75rem 0;
                padding-left: 0;
                list-style: none;
            }
            .message-content ol {
                margin: 0.75rem 0;
                padding-left: 1.5rem;
            }
            .message-content li {
                margin: 0.5rem 0;
                padding: 0.75rem 1rem;
                background: #f8fafc;
                border-left: 3px solid #e2e8f0;
                border-radius: 0 6px 6px 0;
            }
            .message-content ol li {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-left: 3px solid #10b981;
                margin: 0.375rem 0;
                padding: 0.875rem 1.25rem;
                border-radius: 0 6px 6px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            .message-content strong {
                color: #0f172a;
                font-weight: 600;
            }
            .message-content p {
                margin: 0.75rem 0;
                line-height: 1.6;
            }
            .highlight-box {
                background: #1e293b;
                color: white;
                padding: 1.25rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            .highlight-box h2, .highlight-box h3 {
                color: white;
                margin-top: 0;
            }
            .highlight-box ul {
                margin: 0.75rem 0;
            }
            .highlight-box li {
                background: rgba(255, 255, 255, 0.1);
                border-left: 3px solid rgba(255, 255, 255, 0.3);
                color: white;
            }
            .input-section {
                padding: 1.5rem 2rem;
                background: #ffffff;
                border-top: 1px solid #e2e8f0;
            }
            .upload-section {
                margin-bottom: 1rem;
                padding: 1rem;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            .upload-section h3 {
                font-size: 0.875rem;
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.75rem;
            }
            .upload-controls {
                display: flex;
                gap: 1rem;
                align-items: center;
                flex-wrap: wrap;
            }
            .file-input-wrapper {
                position: relative;
                display: inline-block;
            }
            .file-input {
                position: absolute;
                opacity: 0;
                width: 0.1px;
                height: 0.1px;
                overflow: hidden;
            }
            .file-input-label {
                display: inline-block;
                padding: 0.5rem 1rem;
                background: #1e293b;
                color: white;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.875rem;
                font-weight: 500;
                transition: background 0.2s ease;
            }
            .file-input-label:hover {
                background: #334155;
            }
            .file-name {
                color: #64748b;
                font-size: 0.875rem;
                margin-left: 0.5rem;
            }
            .restaurant-input {
                padding: 0.5rem 0.75rem;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 0.875rem;
                width: 200px;
            }
            .upload-btn {
                padding: 0.5rem 1rem;
                background: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.875rem;
                font-weight: 500;
                transition: background 0.2s ease;
            }
            .upload-btn:hover {
                background: #059669;
            }
            .upload-btn:disabled {
                background: #9ca3af;
                cursor: not-allowed;
            }
            .progress-container {
                margin-top: 0.75rem;
                display: none;
            }
            .progress-bar {
                width: 100%;
                height: 6px;
                background: #e5e7eb;
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }
            .progress-fill {
                height: 100%;
                background: #10b981;
                border-radius: 3px;
                width: 0%;
                transition: width 0.3s ease;
            }
            .progress-text {
                font-size: 0.75rem;
                color: #6b7280;
                text-align: center;
            }
            .input-form {
                display: flex;
                gap: 0.75rem;
                align-items: flex-end;
            }
            .input-wrapper {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .query-input {
                width: 100%;
                padding: 0.875rem 1rem;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 0.875rem;
                resize: none;
                min-height: 44px;
                max-height: 120px;
                font-family: inherit;
            }
            .query-input:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            .send-btn {
                padding: 0.875rem 1.5rem;
                background: #1e293b;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.875rem;
                font-weight: 600;
                transition: all 0.2s ease;
                white-space: nowrap;
            }
            .send-btn:hover {
                background: #334155;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(30, 41, 59, 0.15);
            }
            .send-btn:disabled {
                background: #9ca3af;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .info-panel {
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                padding: 1rem;
                margin-bottom: 1rem;
                border-radius: 8px;
                font-size: 0.875rem;
                color: #1e40af;
            }
            .powered-by {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                font-size: 0.875rem;
                color: #64748b;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            .powered-by .ioms {
                color: #1e293b;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">SmartChefBot</div>
            <ul class="navbar-links">
                <li><a href="/">Home</a></li>
                <li><a href="/chat" class="active">Chat</a></li>
                <li><a href="/data">Data</a></li>
            </ul>
        </nav>
        
        <div class="header">
            <h1>SmartChefBot</h1>
            <p>AI-powered restaurant operations, menu optimization & compliance assistance</p>
        </div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="info-panel">
                    <strong>Example questions:</strong><br>
                    • "What items should I put on discount if my chicken is expiring?"<br>
                    • "How can I improve my menu for better profitability?"<br>
                    • "What are the HACCP compliance requirements for my menu?"<br>
                    • "Analyze my menu for food safety risks"
                </div>
            </div>
            
            <div class="input-section">
                <div class="upload-section">
                    <h3>Upload Menu PDF</h3>
                    <div class="upload-controls">
                        <div class="file-input-wrapper">
                            <input type="file" id="menuFile" class="file-input" accept=".pdf">
                            <label for="menuFile" class="file-input-label">Choose PDF</label>
                        </div>
                        <span class="file-name" id="fileName">No file selected</span>
                        <input type="text" id="restaurantName" class="restaurant-input" placeholder="Restaurant name">
                        <button id="uploadBtn" class="upload-btn" disabled>Upload</button>
                    </div>
                    <div class="progress-container" id="progressContainer">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <div class="progress-text" id="progressText">0%</div>
                    </div>
                </div>
                
                <form class="input-form" id="queryForm">
                    <div class="input-wrapper">
                        <textarea 
                            id="queryInput" 
                            class="query-input" 
                            placeholder="Ask a question about menu compliance, business operations, or get recommendations..."
                            rows="1"
                        ></textarea>
                    </div>
                    <button type="submit" id="sendBtn" class="send-btn">Send</button>
                </form>
            </div>
        </div>
        
        <div class="powered-by">
            Powered by <span class="ioms">IOMS</span>
        </div>
        
        <script>
            const chatMessages = document.getElementById('chatMessages');
            const queryForm = document.getElementById('queryForm');
            const queryInput = document.getElementById('queryInput');
            const sendBtn = document.getElementById('sendBtn');
            const menuFile = document.getElementById('menuFile');
            const fileName = document.getElementById('fileName');
            const restaurantName = document.getElementById('restaurantName');
            const uploadBtn = document.getElementById('uploadBtn');
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            let isProcessing = false;
            
            // Auto-resize textarea
            queryInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
            
            // File selection
            menuFile.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileName.textContent = this.files[0].name;
                    uploadBtn.disabled = false;
                } else {
                    fileName.textContent = 'No file selected';
                    uploadBtn.disabled = true;
                }
            });
            
            // Upload functionality
            uploadBtn.addEventListener('click', async function() {
                if (!menuFile.files[0] || !restaurantName.value.trim()) {
                    alert('Please select a file and enter restaurant name');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', menuFile.files[0]);
                formData.append('restaurant_name', restaurantName.value.trim());
                
                uploadBtn.disabled = true;
                uploadBtn.textContent = 'Uploading...';
                progressContainer.style.display = 'block';
                
                // Simulate progress
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressFill.style.width = progress + '%';
                    progressText.textContent = Math.round(progress) + '%';
                }, 200);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    clearInterval(progressInterval);
                    progressFill.style.width = '100%';
                    progressText.textContent = '100%';
                    
                    setTimeout(() => {
                        if (result.success) {
                            addMessage('Successfully processed PDF with Gemini! Extracted ' + result.message.split(' ')[5] + ' menu items.', false);
                            menuFile.value = '';
                            restaurantName.value = '';
                            fileName.textContent = 'No file selected';
                        } else {
                            addMessage('Upload failed: ' + result.message, false);
                        }
                        
                        uploadBtn.disabled = false;
                        uploadBtn.textContent = 'Upload';
                        progressContainer.style.display = 'none';
                        progressFill.style.width = '0%';
                        progressText.textContent = '0%';
                    }, 500);
                    
                } catch (error) {
                    clearInterval(progressInterval);
                    addMessage('Upload error: ' + error.message, false);
                    uploadBtn.disabled = false;
                    uploadBtn.textContent = 'Upload';
                    progressContainer.style.display = 'none';
                }
            });
            
            // Query submission
            queryForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const query = queryInput.value.trim();
                if (!query || isProcessing) return;
                
                isProcessing = true;
                sendBtn.disabled = true;
                sendBtn.textContent = 'Sending...';
                
                // Add user message
                addMessage(query, true);
                queryInput.value = '';
                queryInput.style.height = 'auto';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: query })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        addMessage(result.response, false);
                    } else {
                        addMessage('Error: ' + result.error, false);
                    }
                    
                } catch (error) {
                    addMessage('Network error: ' + error.message, false);
                } finally {
                    isProcessing = false;
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send';
                    queryInput.focus();
                }
            });
            
            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = isUser ? 'U' : 'B';
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = content;
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(contentDiv);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Focus input on load
            queryInput.focus();
            
            // Welcome message
            setTimeout(() => {
                addMessage('Hello! I am SmartChefBot, your AI restaurant assistant. I can help you with business operations, menu optimization, inventory management, and food safety compliance. Upload a menu or ask me anything!', false);
            }, 500);
        </script>
        
        <div class="powered-by">
            Powered by <span class="ioms">IOMS</span>
        </div>
    </body>
    </html>
    """


@app.get("/data", response_class=HTMLResponse)
async def data():
    """Serve the data view interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartChefBot - Data View</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #f8fafc;
                min-height: 100vh;
                padding: 2rem;
            }
            .navbar {
                background: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                padding: 1rem 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
                border-radius: 8px;
            }
            .navbar-brand {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1e293b;
            }
            .navbar-nav {
                display: flex;
                gap: 2rem;
                list-style: none;
            }
            .navbar-nav a {
                text-decoration: none;
                color: #64748b;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
            }
            .navbar-nav a:hover, .navbar-nav a.active {
                color: #1e293b;
                background: #f1f5f9;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 3rem;
            }
            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: #0f172a;
            }
            .header p {
                font-size: 1.125rem;
                color: #64748b;
            }
            .data-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                margin-bottom: 3rem;
            }
            .data-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 2rem;
                transition: all 0.2s ease;
            }
            .data-card:hover {
                border-color: #cbd5e1;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            .data-card h3 {
                color: #0f172a;
                margin-bottom: 1rem;
                font-size: 1.25rem;
                font-weight: 600;
            }
            .data-card p {
                color: #64748b;
                margin-bottom: 1rem;
            }
            .btn {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: #1e293b;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.2s ease;
                border: none;
                cursor: pointer;
                font-size: 0.875rem;
            }
            .btn:hover {
                background: #334155;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(30, 41, 59, 0.15);
            }
            .btn-danger {
                background: #dc2626;
            }
            .btn-danger:hover {
                background: #b91c1c;
            }
            .powered-by {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                font-size: 0.875rem;
                color: #64748b;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            .powered-by .ioms {
                color: #1e293b;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">SmartChefBot</div>
            <ul class="navbar-nav">
                <li><a href="/">Home</a></li>
                <li><a href="/chat">Chat</a></li>
                <li><a href="/data" class="active">Data</a></li>
            </ul>
        </nav>
        
        <div class="container">
            <div class="header">
                <h1>Data Management</h1>
                <p>View and manage your restaurant menu data</p>
            </div>
            
            <div class="data-grid">
                <div class="data-card">
                    <h3>View Menu Data</h3>
                    <p>Browse all uploaded menu items and restaurant data in a structured format.</p>
                    <button class="btn" onclick="loadMenuData()">Load Data</button>
                </div>
                
                <div class="data-card">
                    <h3>Clear All Data</h3>
                    <p>Remove all uploaded menu files and extracted data. This action cannot be undone.</p>
                    <button class="btn btn-danger" onclick="clearAllData()">Clear All</button>
                </div>
            </div>
            
            <div id="dataContent"></div>
        </div>
        
        <script>
            async function loadMenuData() {
                try {
                    const response = await fetch('/menus');
                    const result = await response.json();
                    
                    if (result.success) {
                        displayMenuData(result.menus);
                    } else {
                        alert('Failed to load menu data: ' + result.error);
                    }
                } catch (error) {
                    alert('Error loading menu data: ' + error.message);
                }
            }
            
            function displayMenuData(menus) {
                const content = document.getElementById('dataContent');
                
                if (menus.length === 0) {
                    content.innerHTML = '<div class="data-card"><h3>No Data Available</h3><p>No menu data has been uploaded yet.</p></div>';
                    return;
                }
                
                let html = '<div class="data-card"><h3>Menu Data (' + menus.length + ' restaurants)</h3>';
                
                menus.forEach((menu, index) => {
                    html += '<div style="margin-bottom: 2rem; padding: 1rem; background: #f8fafc; border-radius: 8px;">';
                    html += '<h4 style="color: #1e293b; margin-bottom: 1rem;">' + menu.restaurant_name + '</h4>';
                    html += '<p style="color: #64748b; margin-bottom: 1rem;">Items: ' + menu.items.length + '</p>';
                    html += '<div style="max-height: 300px; overflow-y: auto;">';
                    
                    menu.items.forEach(item => {
                        html += '<div style="padding: 0.75rem; background: white; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 0.5rem;">';
                        html += '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">';
                        html += '<strong style="color: #1e293b;">' + item.name + '</strong>';
                        html += '<span style="color: #10b981; font-weight: 600;">' + item.price + '</span>';
                        html += '</div>';
                        html += '<p style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.5rem;">' + item.description + '</p>';
                        html += '<span style="color: #6b7280; font-size: 0.75rem;">' + item.category + '</span>';
                        html += '</div>';
                    });
                    
                    html += '</div></div>';
                });
                
                html += '</div>';
                content.innerHTML = html;
            }
            
            async function clearAllData() {
                const confirmed = confirm('Are you sure you want to delete ALL menu data?\n\nThis will permanently remove:\n- All extracted JSON files\n- All uploaded PDF files\n- All menu items data\n\nThis action cannot be undone!');
                
                if (confirmed) {
                    try {
                        const response = await fetch('/clear', { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.success) {
                            alert('All data cleared successfully!');
                            document.getElementById('dataContent').innerHTML = '';
                        } else {
                            alert('Failed to clear data: ' + result.error);
                        }
                    } catch (error) {
                        alert('Error clearing data: ' + error.message);
                    }
                }
            }
        </script>
        
        <div class="powered-by">
            Powered by <span class="ioms">IOMS</span>
        </div>
    </body>
    </html>
    """


@app.post("/query", response_class=JSONResponse)
async def query(request: QueryRequest):
    """Process a user query"""
    try:
        result = get_executor().run(request.query, request.context)
        return QueryResponse(
            success=True,
            response=result["response"],
            iterations_used=result.get("iterations_used"),
            scratchpad=result.get("scratchpad")
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            response="",
            error=str(e)
        )


@app.post("/upload", response_class=JSONResponse)
async def upload_menu(file: UploadFile = File(...), restaurant_name: str = Form(...)):
    """Upload and process a menu PDF"""
    try:
        # Save uploaded file
        upload_dir = Path(__file__).parent / "data" / "menus"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{restaurant_name}.pdf"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with menu tool
        result = get_menu_tool().upload_menu(str(file_path), restaurant_name)
        
        return MenuUploadResponse(
            success=True,
            message=f"Successfully processed PDF with Gemini! Extracted {result['item_count']} menu items.",
            restaurant_name=restaurant_name
        )
    except Exception as e:
        return MenuUploadResponse(
            success=False,
            message=f"Upload failed: {str(e)}"
        )


@app.get("/menus", response_class=JSONResponse)
async def get_menus():
    """Get all uploaded menu data"""
    try:
        menus = get_menu_tool().list_menus()
        return MenuListResponse(
            success=True,
            menus=menus,
            count=len(menus)
        )
    except Exception as e:
        return MenuListResponse(
            success=False,
            menus=[],
            count=0
        )


@app.post("/clear", response_class=JSONResponse)
async def clear_data():
    """Clear all menu data"""
    try:
        get_menu_tool().clear_all_data()
        return {"success": True, "message": "All data cleared successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SmartChefBot"}


if __name__ == "__main__":
    import socket
    
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 3000))
    
    # Get local IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "YOUR_IP_ADDRESS"
    
    print("Starting SmartChefBot Server")
    print("=" * 70)
    print("✓ Server is running and accessible on your network!")
    print("")
    print("Access from THIS computer:")
    print(f"  → http://localhost:{port}")
    print(f"  → http://localhost:{port}/chat (Chat Interface)")
    print(f"  → http://localhost:{port}/docs (API Documentation)")
    print("")
    print("Access from OTHER computers on same network:")
    print(f"  → http://{local_ip}:{port}")
    print(f"  → http://{local_ip}:{port}/chat (Chat Interface)")
    print(f"  → http://{local_ip}:{port}/docs (API Documentation)")
    print("")
    print(f"Share this address with colleagues: http://{local_ip}:{port}")
    print("")
    print("Note: First query will take time (downloading LLM model)")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=port)