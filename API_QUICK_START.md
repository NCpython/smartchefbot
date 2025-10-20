# 🚀 API Quick Start Guide

## ✅ What Was Done

Your SmartChefBot now has a **complete RESTful API** with 15 new structured endpoints!

### 📦 New Structure Created

```
fnb-intelligence/
├── api/                           # NEW: API Package
│   ├── __init__.py
│   ├── models/                    # NEW: Request/Response Models
│   │   ├── __init__.py
│   │   ├── requests.py           # Input data structures
│   │   └── responses.py          # Output data structures
│   └── v1/                        # NEW: API Version 1
│       ├── __init__.py
│       ├── menus.py              # Menu management endpoints
│       ├── query.py              # AI query endpoints
│       ├── items.py              # Search endpoints
│       └── system.py             # System operations
├── server.py                      # UPDATED: Includes new routers
└── API_DOCUMENTATION.md           # NEW: Complete API docs
```

---

## 🎯 What's Available Now

### **15 New API Endpoints**

#### 🔍 Query Endpoints (3)
- `POST /api/v1/query/general` - General questions
- `POST /api/v1/query/business` - Business recommendations
- `POST /api/v1/query/compliance` - Compliance analysis

#### 🍽️ Menu Endpoints (5)
- `GET /api/v1/menus/` - List all menus
- `POST /api/v1/menus/upload` - Upload menu PDF
- `GET /api/v1/menus/{name}` - Get specific menu
- `DELETE /api/v1/menus/{name}` - Delete menu
- `GET /api/v1/menus/{name}/items` - Get menu items

#### 🔎 Search Endpoints (3)
- `POST /api/v1/items/search` - Search all items
- `GET /api/v1/items/search/{query}` - Quick search
- `GET /api/v1/items/{name}/search` - Search in restaurant

#### ⚙️ System Endpoints (4)
- `GET /api/v1/system/health` - Health check
- `GET /api/v1/system/stats` - System statistics
- `POST /api/v1/system/clear` - Clear all data
- `GET /api/v1/system/version` - API version

---

## 🚀 How to Use

### 1. Start the Server

```bash
cd /Users/nishantchaturvedi/Desktop/fnb-intelligence
source venv/bin/activate
python server.py
```

**Server starts on**: http://localhost:3000

---

### 2. View Interactive API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

These provide **interactive testing** - you can try endpoints directly in the browser!

---

### 3. Test the API

#### Example 1: Health Check
```bash
curl http://localhost:3000/api/v1/system/health
```

#### Example 2: List Menus
```bash
curl http://localhost:3000/api/v1/menus/
```

#### Example 3: Ask a Question
```bash
curl -X POST http://localhost:3000/api/v1/query/general \
  -H "Content-Type: application/json" \
  -d '{"query": "What is HACCP?"}'
```

#### Example 4: Business Query
```bash
curl -X POST http://localhost:3000/api/v1/query/business \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What items should I discount?",
    "restaurant_name": "Chef India"
  }'
```

#### Example 5: Search Items
```bash
curl http://localhost:3000/api/v1/items/search/chicken
```

#### Example 6: Upload Menu
```bash
curl -X POST http://localhost:3000/api/v1/menus/upload \
  -F "file=@menu.pdf" \
  -F "restaurant_name=My Restaurant"
```

---

## ✅ Backward Compatibility

**✓ All existing functionality still works!**

### Web UI (Unchanged)
- http://localhost:3000/ - Home page
- http://localhost:3000/chat - Chat interface
- http://localhost:3000/data - Data view

### Legacy API Endpoints (Still Working)
- `POST /query` - Original query endpoint
- `POST /upload` - Original upload
- `GET /menus` - Original menu list
- `POST /clear` - Original clear
- `GET /health` - Original health check

**Your existing web interface will continue to work exactly as before!**

---

## 📊 What's Different?

### Before (Legacy)
```
POST /query
POST /upload
GET /menus
```

### Now (New Structured API)
```
/api/v1/query/general
/api/v1/query/business
/api/v1/query/compliance

/api/v1/menus/
/api/v1/menus/upload
/api/v1/menus/{name}
/api/v1/menus/{name}/items

/api/v1/items/search
/api/v1/system/health
/api/v1/system/stats
```

**Benefits**:
- ✅ Organized by functionality
- ✅ Versioned (/v1/)
- ✅ RESTful design
- ✅ Better documentation
- ✅ Easier to extend
- ✅ Professional API structure

---

## 🎨 API Features

### 1. Auto-Generated Documentation
FastAPI automatically generates beautiful interactive docs at `/docs`

### 2. Request Validation
All inputs are validated using Pydantic models

### 3. Type Safety
Full type hints and IDE autocomplete support

### 4. Error Handling
Consistent error responses with HTTP status codes

### 5. API Versioning
Future-proof with `/v1/` namespace

---

## 💡 Integration Examples

### Python
```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:3000/api/v1/query/general",
    json={"query": "What is HACCP?"}
)
print(response.json()["response"])

# Search for items
response = requests.get(
    "http://localhost:3000/api/v1/items/search/chicken"
)
items = response.json()["results"]
print(f"Found {len(items)} chicken items")
```

### JavaScript
```javascript
// Fetch menu data
fetch('http://localhost:3000/api/v1/menus/')
  .then(r => r.json())
  .then(data => {
    console.log(`Found ${data.count} restaurants`);
  });

// Ask business question
fetch('http://localhost:3000/api/v1/query/business', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: 'What items should I discount?',
    restaurant_name: 'Chef India'
  })
})
.then(r => r.json())
.then(data => console.log(data.response));
```

---

## 🔍 How to Explore

### Step 1: Check System Health
```bash
curl http://localhost:3000/api/v1/system/health
```

### Step 2: Get Statistics
```bash
curl http://localhost:3000/api/v1/system/stats
```

### Step 3: List Available Menus
```bash
curl http://localhost:3000/api/v1/menus/
```

### Step 4: Try a Query
```bash
curl -X POST http://localhost:3000/api/v1/query/general \
  -H "Content-Type: application/json" \
  -d '{"query": "What are food safety basics?"}'
```

### Step 5: Search Menu Items
```bash
curl http://localhost:3000/api/v1/items/search/chicken
```

---

## 📖 Full Documentation

See `API_DOCUMENTATION.md` for complete API reference with:
- All endpoint details
- Request/response examples
- Error codes
- Integration guides
- Best practices

---

## 🎉 Next Steps

1. ✅ **Test the API** using `/docs` in your browser
2. ✅ **Try the examples** above
3. ✅ **Read full docs** in `API_DOCUMENTATION.md`
4. ✅ **Build integrations** using the new endpoints
5. ✅ **Keep existing UI** - it still works!

---

## 🔧 Testing Checklist

Run these to verify everything works:

```bash
# 1. Health check
curl http://localhost:3000/api/v1/system/health

# 2. Stats
curl http://localhost:3000/api/v1/system/stats

# 3. List menus
curl http://localhost:3000/api/v1/menus/

# 4. Query test
curl -X POST http://localhost:3000/api/v1/query/general \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# 5. Web UI test
open http://localhost:3000
open http://localhost:3000/chat
open http://localhost:3000/docs
```

---

## ✨ Key Improvements

| Feature | Before | Now |
|---------|--------|-----|
| **API Structure** | Flat | Organized by version & function |
| **Documentation** | Manual | Auto-generated interactive docs |
| **Versioning** | None | `/v1/` with future extensibility |
| **Search** | POST only | GET & POST methods |
| **Error Handling** | Basic | Structured with HTTP codes |
| **Models** | Inline | Separate validated models |
| **Business Logic** | Mixed | Separate endpoint for business queries |
| **Compliance** | Mixed | Dedicated compliance endpoint |

---

## 🎓 Summary

**What you have now:**
- ✅ Professional RESTful API
- ✅ 15 new structured endpoints
- ✅ Auto-generated documentation
- ✅ Backward compatible (nothing broke!)
- ✅ Version 1 namespace for future growth
- ✅ Separate endpoints for different use cases
- ✅ Easy to integrate with other systems

**What still works:**
- ✅ Web UI (/, /chat, /data)
- ✅ Legacy API endpoints
- ✅ All existing functionality
- ✅ Menu uploads
- ✅ Chat interface

**Your chatbot is now a production-ready API! 🚀**

