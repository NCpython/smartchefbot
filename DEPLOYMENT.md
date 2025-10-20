# 🚀 Deployment Guide - Railway

This guide will help you deploy SmartChefBot to Railway for MVP testing.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account
- ✅ Railway account (sign up at https://railway.app)
- ✅ Google Gemini API key (get from https://makersuite.google.com/app/apikey)

---

## 🔧 Step 1: Prepare Your Code

Your code is already configured for Railway deployment! Here's what was set up:

### Files Created:
- ✅ `.gitignore` - Excludes venv, __pycache__, uploaded PDFs, etc.
- ✅ `railway.json` - Railway configuration
- ✅ `data/menus/.gitkeep` - Keeps directory structure in Git
- ✅ `data/extracted/.gitkeep` - Keeps directory structure in Git
- ✅ `LICENSE` - MIT License

### Code Updates:
- ✅ `server.py` now reads `PORT` from environment variable
- ✅ All dependencies listed in `requirements.txt`

---

## 📦 Step 2: Push to GitHub

### Initialize Git (if not already done):

```bash
cd /Users/nishantchaturvedi/Desktop/fnb-intelligence
git init
```

### Add all files:

```bash
git add .
```

### Verify venv is excluded:

```bash
git status
```

**Important:** You should NOT see `venv/` in the list. If you do, check `.gitignore`.

### Create .env file (DO NOT COMMIT THIS):

Create a `.env` file locally for your own reference:

```bash
cat > .env << 'EOF'
GOOGLE_API_KEY=your_actual_api_key_here
PORT=3000
EOF
```

**Note:** `.env` is in `.gitignore` and will NOT be committed.

### Commit your code:

```bash
git commit -m "Initial commit: SmartChefBot ready for Railway deployment

Features:
- Python FastAPI backend with AI chatbot
- Google Gemini AI integration for menu extraction
- PDF menu upload and processing
- RESTful API with 15+ endpoints
- Web UI with chat interface
- Business operations and compliance features
- Railway deployment configuration"
```

### Create GitHub Repository:

1. Go to https://github.com/new
2. Repository name: `smartchefbot` (or your preferred name)
3. Description: "AI-powered restaurant menu analysis and compliance chatbot"
4. **Do NOT initialize with README** (you already have one)
5. Keep it Public or Private (your choice)
6. Click "Create repository"

### Push to GitHub:

```bash
# Replace YOUR_USERNAME with your GitHub username
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smartchefbot.git
git push -u origin main
```

---

## 🚂 Step 3: Deploy to Railway

### 3.1 Sign Up / Login

1. Go to https://railway.app
2. Click **"Login with GitHub"**
3. Authorize Railway to access your GitHub account

### 3.2 Create New Project

1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `smartchefbot`
4. Railway will automatically detect it's a Python project

### 3.3 Railway Auto-Detection

Railway's Nixpacks will automatically:
- ✅ Detect Python from `requirements.txt`
- ✅ Install Python 3.11
- ✅ Install all dependencies: `pip install -r requirements.txt`
- ✅ Start the server: `uvicorn server:app --host 0.0.0.0 --port $PORT`

You'll see build logs like:
```
✓ Detected Python
✓ Installing dependencies from requirements.txt
✓ Building with Nixpacks
✓ Starting application
✓ Deployment successful
```

### 3.4 Add Environment Variables

**Critical Step:** Add your Google Gemini API key

1. In Railway dashboard, click on your service
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add:
   - **Variable:** `GOOGLE_API_KEY`
   - **Value:** `your_actual_gemini_api_key`
5. Click **"Add"**

Railway will automatically redeploy with the new environment variable.

### 3.5 Get Your URL

1. Go to **"Settings"** tab
2. Under **"Networking"**, click **"Generate Domain"**
3. Railway will create a URL like:
   ```
   https://smartchefbot-production-xxxx.up.railway.app
   ```
4. Copy this URL - this is your live API!

### 3.6 (Optional) Add Custom Domain

If you want a custom domain like `api.yourcompany.com`:

1. In **"Settings"** → **"Networking"**
2. Click **"Custom Domain"**
3. Enter your domain
4. Add CNAME record to your DNS:
   ```
   CNAME: api.yourcompany.com → xxxx.up.railway.app
   ```

---

## ✅ Step 4: Test Your Deployment

### Test Health Endpoint:

```bash
curl https://YOUR-APP.up.railway.app/health
```

**Expected Response:**
```json
{"status": "healthy", "service": "SmartChefBot"}
```

### Open Web Interface:

Open in your browser:
```
https://YOUR-APP.up.railway.app/
https://YOUR-APP.up.railway.app/chat
https://YOUR-APP.up.railway.app/docs
```

### Test API Endpoints:

```bash
# List menus
curl https://YOUR-APP.up.railway.app/api/v1/menus/

# Ask a question
curl -X POST https://YOUR-APP.up.railway.app/api/v1/query/general \
  -H "Content-Type: application/json" \
  -d '{"query": "What is HACCP?"}'

# System stats
curl https://YOUR-APP.up.railway.app/api/v1/system/stats
```

---

## 🔄 Step 5: Automatic Deployments

Railway is now connected to your GitHub repository!

**Every time you push to GitHub:**
1. Railway automatically detects the push
2. Builds your application
3. Deploys the new version
4. Zero downtime deployment

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push

# Railway automatically deploys! ✨
```

---

## 📊 Step 6: Monitor Your Application

### View Logs:

1. Go to Railway dashboard
2. Click your service
3. Go to **"Logs"** tab
4. See real-time application logs

### View Metrics:

1. Go to **"Metrics"** tab
2. See:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

### Set Up Alerts (Optional):

1. Go to **"Settings"**
2. Add webhook for deployment notifications
3. Get notified via Slack/Discord/Email

---

## 💰 Railway Pricing

### Free Tier:
- ✅ **$5 credit per month**
- ✅ Enough for MVP testing
- ✅ ~500 hours of runtime
- ✅ 1 GB RAM
- ✅ 1 GB disk

**Your app should stay within free tier during testing!**

### If You Exceed:
- Additional usage is billed
- ~$5-10/month for light usage
- You can set spending limits

---

## 🐛 Troubleshooting

### Build Failed:

**Check logs in Railway dashboard:**
- Look for missing dependencies
- Check Python version compatibility
- Verify `requirements.txt` is correct

**Common issues:**
```bash
# If build fails, verify locally first:
cd /Users/nishantchaturvedi/Desktop/fnb-intelligence
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

### Application Won't Start:

**Check environment variables:**
- Ensure `GOOGLE_API_KEY` is set in Railway
- Check Railway logs for error messages

**Verify locally:**
```bash
export GOOGLE_API_KEY=your_key
export PORT=3000
python server.py
```

### Port Issues:

Your app is configured to use `$PORT` environment variable.
Railway automatically sets this. No action needed!

### Uploaded Files Not Persisting:

Railway's filesystem is ephemeral. Files reset on each deploy.

**Solution:** Add Railway Volume (optional for MVP):
1. Go to **"Volumes"** tab
2. Click **"New Volume"**
3. Mount path: `/app/data`
4. Size: 1 GB (free tier limit)

---

## 🔒 Security Notes (For Later)

Your current deployment is **open** (no authentication). This is fine for MVP testing.

**For production, you'll need to add:**
- API key authentication
- Rate limiting
- CORS restrictions
- HTTPS only (Railway provides this by default ✅)
- Input validation (FastAPI provides this ✅)

We'll implement these in Phase 2 when moving to production!

---

## 📚 Useful Commands

### Local Development:
```bash
# Run locally
python server.py

# Access locally
open http://localhost:3000
```

### Git Operations:
```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Your message"

# Push (triggers Railway deployment)
git push
```

### Railway CLI (Optional):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Open dashboard
railway open
```

---

## 🎯 What's Next?

After successful deployment, you can:

1. ✅ Share the URL with your team
2. ✅ Test with enterprise tool integrations
3. ✅ Upload menu PDFs via `/chat` interface
4. ✅ Make API calls from your enterprise tools
5. ✅ Monitor usage in Railway dashboard

### Example API Integration:

```python
import requests

# Your deployed API URL
API_URL = "https://your-app.up.railway.app"

# Query the AI
response = requests.post(
    f"{API_URL}/api/v1/query/general",
    json={"query": "What are food safety best practices?"}
)

print(response.json()["response"])
```

---

## 📞 Support

### Railway Issues:
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Application Issues:
- Check logs in Railway dashboard
- Test locally first
- Verify environment variables are set

---

## ✨ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] `GOOGLE_API_KEY` environment variable set
- [ ] Domain generated
- [ ] Health check passes: `/health`
- [ ] Web interface loads: `/`
- [ ] Chat interface works: `/chat`
- [ ] API docs accessible: `/docs`
- [ ] Can upload menu PDF
- [ ] Can query the AI

**Once all checked, you're live! 🚀**

---

**Need help?** Check the logs in Railway dashboard or test locally first!

Good luck with your MVP deployment! 🎉

