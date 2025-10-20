# 🚂 Railway Deployment - Quick Start

**⏱️ Total Time: ~10 minutes**

---

## ✅ Pre-flight Checklist

- [ ] GitHub account
- [ ] Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- [ ] Code is ready (you're all set! ✨)

---

## 🚀 Deploy in 3 Steps

### Step 1: Push to GitHub (5 minutes)

```bash
cd /Users/nishantchaturvedi/Desktop/fnb-intelligence

# Initialize Git
git init

# Add files (venv is automatically excluded!)
git add .

# Verify venv is NOT included
git status

# Commit
git commit -m "Initial commit: SmartChefBot for Railway"

# Create repo on GitHub.com (don't initialize with README)
# Then push:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smartchefbot.git
git push -u origin main
```

---

### Step 2: Deploy to Railway (3 minutes)

1. **Go to** https://railway.app
2. **Click** "Login with GitHub"
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your `smartchefbot` repository
6. **Wait** for Railway to auto-detect and build (2-3 minutes)

---

### Step 3: Add API Key (2 minutes)

1. **In Railway dashboard**, click your service
2. **Go to** "Variables" tab
3. **Click** "New Variable"
4. **Add:**
   - Key: `GOOGLE_API_KEY`
   - Value: `your_actual_api_key`
5. **Click** "Add"
6. **Go to** "Settings" → "Networking"
7. **Click** "Generate Domain"

---

## ✨ You're Live!

Your app is now at:
```
https://smartchefbot-production-xxxx.up.railway.app
```

### Test it:

```bash
# Health check
curl https://YOUR-APP.up.railway.app/health

# Open in browser
open https://YOUR-APP.up.railway.app
open https://YOUR-APP.up.railway.app/chat
open https://YOUR-APP.up.railway.app/docs
```

---

## 🔄 Continuous Deployment

**Now every time you push to GitHub, Railway auto-deploys!**

```bash
# Make changes
git add .
git commit -m "Updated feature"
git push

# Railway automatically deploys! 🎉
```

---

## 📊 Key URLs

| Page | URL |
|------|-----|
| Home | `https://YOUR-APP.up.railway.app/` |
| Chat | `https://YOUR-APP.up.railway.app/chat` |
| Data | `https://YOUR-APP.up.railway.app/data` |
| API Docs | `https://YOUR-APP.up.railway.app/docs` |
| Health | `https://YOUR-APP.up.railway.app/health` |

---

## 🔧 Important Files Created

✅ `.gitignore` - Excludes venv, __pycache__, .env  
✅ `railway.json` - Railway configuration  
✅ `data/menus/.gitkeep` - Directory placeholder  
✅ `data/extracted/.gitkeep` - Directory placeholder  
✅ `LICENSE` - MIT License  
✅ `server.py` - Updated to use PORT env variable  

---

## 💡 What Railway Does

Railway automatically:
- ✅ Detects Python from `requirements.txt`
- ✅ Installs Python 3.11
- ✅ Runs: `pip install -r requirements.txt`
- ✅ Starts: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- ✅ Provides HTTPS URL
- ✅ Auto-restarts on failures
- ✅ Auto-deploys on Git push

**No Docker needed! No complex config!**

---

## 💰 Cost

**Free Tier:**
- $5 credit/month
- Perfect for MVP testing
- ~500 hours runtime
- 1 GB RAM

**Your app:** Should stay within free tier! 🎉

---

## 🐛 Troubleshooting

**Build failed?**
- Check Railway logs
- Verify locally: `python server.py`

**App won't start?**
- Check `GOOGLE_API_KEY` is set in Railway
- View logs in Railway dashboard

**Need help?**
- See full guide: `DEPLOYMENT.md`
- Railway docs: https://docs.railway.app

---

## 🎯 Next Steps

After deployment:
1. ✅ Test the chat interface
2. ✅ Upload a menu PDF
3. ✅ Try API endpoints from `/docs`
4. ✅ Integrate with your enterprise tools
5. ✅ Share URL with your team

---

**Ready to deploy? Let's go! 🚀**

For detailed instructions, see `DEPLOYMENT.md`

