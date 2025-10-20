# 🚀 SmartChefBot API Documentation

## Overview

The SmartChefBot API provides RESTful endpoints for restaurant intelligence, menu management, and compliance analysis.

**Base URL**: `http://localhost:3000`

**API Version**: v1

**Auto-Generated Docs**:
- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc

---

## 📋 API Structure

```
/api/v1/
├── /query/          → AI Query Processing
├── /menus/          → Menu Management
├── /items/          → Menu Item Search
└── /system/         → System Operations
```

---

## 🔍 Query Endpoints

### 1. General Query
Process general questions about restaurant operations and compliance.

**Endpoint**: `POST /api/v1/query/general`

**Request Body**:
```json
{
  "query": "What are the food safety requirements for restaurants?",
  "context": {}  // optional
}
```

**Response**:
```json
{
  "success": true,
  "response": "Food safety requirements include...",
  "iterations_used": 2,
  "scratchpad": ["Iteration 1: Processing query", "Iteration 2: Generated response"],
  "metadata": {
    "max_iterations": 5,
    "query_type": "general"
  }
}
```

---

### 2. Business Operations Query
Get business recommendations based on your menu data (HYBRID MODE).

**Endpoint**: `POST /api/v1/query/business`

**Request Body**:
```json
{
  "query": "My chicken is expiring today, what items should I discount?",
  "restaurant_name": "Chef India",  // optional
  "context": {}  // optional
}
```

**Response**:
```json
{
  "success": true,
  "response": "Here are my recommendations for your expiring chicken...",
  "menu_items_analyzed": 12,
  "recommendations": null,
  "iterations_used": 3
}
```

**Use Cases**:
- Discount recommendations
- Inventory management
- Waste reduction
- Promotion planning
- Ingredient-based queries

---

### 3. Compliance Analysis Query
Analyze your menu for HACCP and food safety compliance (HYBRID MODE).

**Endpoint**: `POST /api/v1/query/compliance`

**Request Body**:
```json
{
  "query": "How can I make my menu HACCP compliant?",
  "restaurant_name": "Chef India",  // optional
  "standards": ["HACCP", "Food Safety"]  // optional
}
```

**Response**:
```json
{
  "success": true,
  "response": "Your menu needs the following HACCP improvements...",
  "menu_items_analyzed": 12,
  "compliance_issues": null,
  "compliance_score": null
}
```

---

## 🍽️ Menu Endpoints

### 1. List All Menus
Get all uploaded restaurant menus.

**Endpoint**: `GET /api/v1/menus/`

**Response**:
```json
{
  "success": true,
  "menus": [
    {
      "restaurant_name": "Chef India",
      "items": [...],
      "total_items": 12
    }
  ],
  "count": 2
}
```

---

### 2. Upload Menu PDF
Upload and process a menu PDF using Gemini AI.

**Endpoint**: `POST /api/v1/menus/upload`

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file`: PDF file
- `restaurant_name`: Restaurant name (string)

**Response**:
```json
{
  "success": true,
  "message": "Successfully processed PDF with Gemini! Extracted 12 menu items.",
  "data": {
    "restaurant_name": "Chef India",
    "item_count": 12
  }
}
```

**Example (curl)**:
```bash
curl -X POST "http://localhost:3000/api/v1/menus/upload" \
  -F "file=@menu.pdf" \
  -F "restaurant_name=Chef India"
```

---

### 3. Get Specific Restaurant Menu
Get all menu items for a specific restaurant.

**Endpoint**: `GET /api/v1/menus/{restaurant_name}`

**Example**: `GET /api/v1/menus/Chef%20India`

**Response**:
```json
{
  "success": true,
  "restaurant_name": "Chef India",
  "items": [
    {
      "name": "Butter Chicken",
      "price": "€12.99",
      "description": "Creamy tomato curry",
      "category": "Main Course",
      "restaurant": "Chef India"
    }
  ],
  "total_items": 12
}
```

---

### 4. Delete Restaurant Menu
Delete all data for a specific restaurant.

**Endpoint**: `DELETE /api/v1/menus/{restaurant_name}`

**Example**: `DELETE /api/v1/menus/Chef%20India`

**Response**:
```json
{
  "success": true,
  "message": "Successfully deleted menu for 'Chef India'",
  "data": {
    "restaurant_name": "Chef India"
  }
}
```

---

### 5. Get Restaurant Items
Alternative endpoint to get all items from a restaurant.

**Endpoint**: `GET /api/v1/menus/{restaurant_name}/items`

**Example**: `GET /api/v1/menus/Chef%20India/items`

Same response as endpoint #3.

---

## 🔍 Items/Search Endpoints

### 1. Search Menu Items (POST)
Search for menu items across all restaurants or in a specific one.

**Endpoint**: `POST /api/v1/items/search`

**Request Body**:
```json
{
  "query": "chicken",
  "restaurant_name": "Chef India",  // optional - search only in this restaurant
  "filters": {}  // optional - additional filters
}
```

**Response**:
```json
{
  "success": true,
  "query": "chicken",
  "results": [
    {
      "name": "Butter Chicken",
      "price": "€12.99",
      "description": "Creamy curry",
      "restaurant": "Chef India"
    }
  ],
  "count": 3,
  "searched_restaurants": ["Chef India", "CCD"]
}
```

---

### 2. Search Menu Items (GET)
Simple search using GET method.

**Endpoint**: `GET /api/v1/items/search/{query}`

**Query Parameters**:
- `restaurant_name` (optional): Search only in this restaurant

**Example**: `GET /api/v1/items/search/chicken?restaurant_name=Chef%20India`

**Response**: Same as POST search endpoint.

---

### 3. Search in Specific Restaurant
Search within a specific restaurant.

**Endpoint**: `GET /api/v1/items/{restaurant_name}/search`

**Query Parameters**:
- `query` (required): Search query

**Example**: `GET /api/v1/items/Chef%20India/search?query=chicken`

**Response**: Same structure as other search endpoints.

---

## ⚙️ System Endpoints

### 1. Health Check
Check if the API is running.

**Endpoint**: `GET /api/v1/system/health`

**Response**:
```json
{
  "status": "healthy",
  "service": "SmartChefBot API",
  "version": "1.0.0",
  "uptime": 3600.52
}
```

---

### 2. System Statistics
Get statistics about uploaded menus.

**Endpoint**: `GET /api/v1/system/stats`

**Response**:
```json
{
  "success": true,
  "total_menus": 5,
  "total_items": 67,
  "restaurants": ["Chef India", "CCD", "Chef", "allowme", "clear"],
  "storage_used": "2.4 MB"
}
```

---

### 3. Clear All Data
Delete all menu data (⚠️ CAUTION: Cannot be undone!)

**Endpoint**: `POST /api/v1/system/clear`

**Response**:
```json
{
  "success": true,
  "message": "All menu data cleared successfully",
  "data": {
    "cleared_menus": true,
    "cleared_pdfs": true
  }
}
```

---

### 4. Get API Version
Get version information.

**Endpoint**: `GET /api/v1/system/version`

**Response**:
```json
{
  "service": "SmartChefBot API",
  "version": "1.0.0",
  "api_version": "v1",
  "description": "AI-powered restaurant intelligence and compliance assistant"
}
```

---

## 🎨 Legacy Endpoints (Backward Compatible)

These endpoints are kept for backward compatibility with the existing web UI:

- `POST /query` - Original query endpoint
- `POST /upload` - Original upload endpoint
- `GET /menus` - Original menus list
- `POST /clear` - Original clear endpoint
- `GET /health` - Original health check

**Note**: New integrations should use the `/api/v1/` endpoints.

---

## 📱 Web UI Routes

These return HTML, not JSON:

- `GET /` - Home page
- `GET /chat` - Chat interface
- `GET /data` - Data view page

---

## 🔐 Error Responses

All errors follow this structure:

```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes**:
- `200` - Success
- `201` - Created (for uploads)
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## 📊 Response Models Summary

### QueryResponse
```json
{
  "success": bool,
  "response": string,
  "iterations_used": int,
  "scratchpad": [string],
  "metadata": object
}
```

### BusinessResponse
```json
{
  "success": bool,
  "response": string,
  "menu_items_analyzed": int,
  "recommendations": array,
  "iterations_used": int
}
```

### MenuResponse
```json
{
  "success": bool,
  "restaurant_name": string,
  "items": [MenuItemResponse],
  "total_items": int
}
```

### SearchResponse
```json
{
  "success": bool,
  "query": string,
  "results": [MenuItemResponse],
  "count": int,
  "searched_restaurants": [string]
}
```

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /Users/nishantchaturvedi/Desktop/fnb-intelligence
python server.py
```

### 2. View Auto-Generated Docs
Open in browser: http://localhost:3000/docs

### 3. Test an Endpoint
```bash
# Health check
curl http://localhost:3000/api/v1/system/health

# List menus
curl http://localhost:3000/api/v1/menus/

# Query
curl -X POST http://localhost:3000/api/v1/query/general \
  -H "Content-Type: application/json" \
  -d '{"query": "What is HACCP?"}'
```

---

## 💡 Integration Examples

### Python (requests)
```python
import requests

# General query
response = requests.post(
    "http://localhost:3000/api/v1/query/general",
    json={"query": "What is HACCP?"}
)
print(response.json())

# Upload menu
files = {"file": open("menu.pdf", "rb")}
data = {"restaurant_name": "My Restaurant"}
response = requests.post(
    "http://localhost:3000/api/v1/menus/upload",
    files=files,
    data=data
)
print(response.json())
```

### JavaScript (fetch)
```javascript
// General query
fetch('http://localhost:3000/api/v1/query/general', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'What is HACCP?'})
})
.then(r => r.json())
.then(data => console.log(data));

// Search items
fetch('http://localhost:3000/api/v1/items/search/chicken')
.then(r => r.json())
.then(data => console.log(data));
```

### cURL Examples
```bash
# Business query
curl -X POST http://localhost:3000/api/v1/query/business \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What items should I discount?",
    "restaurant_name": "Chef India"
  }'

# Search
curl -X POST http://localhost:3000/api/v1/items/search \
  -H "Content-Type: application/json" \
  -d '{"query": "chicken", "restaurant_name": "Chef India"}'

# Get stats
curl http://localhost:3000/api/v1/system/stats
```

---

## 🎯 Best Practices

1. **Use `/api/v1/` endpoints** for new integrations
2. **Check `/docs`** for interactive API documentation
3. **Use POST for searches** when you need filters
4. **Use GET for simple searches** when just passing a query string
5. **Always check `success: true`** in responses
6. **Handle errors gracefully** using HTTP status codes

---

## 📞 Support

- Interactive Docs: http://localhost:3000/docs
- GitHub Issues: [Your repository]
- Email: [Your email]

---

**Built with ❤️ for restaurant owners and compliance professionals**

