# Deployment Guide

## Backend Deployment (Railway)

### Step 1: Prepare Repository
1. Make sure all code is committed to GitHub
2. Ensure `.gitignore` excludes `runs/`, `chroma_db/`, and `.env` files

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python

### Step 3: Configure Environment Variables
In Railway dashboard, add these environment variables:
```
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
```

### Step 4: Configure Build Settings
- **Build Command**: `pip install -r backend/requirements.txt && playwright install chromium`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 5: Deploy
Railway will automatically deploy. Get your backend URL (e.g., `https://your-app.railway.app`)

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Repository
1. Make sure frontend code is in the repo
2. Ensure `package.json` is in `frontend/` directory

### Step 2: Deploy to Vercel
1. Go to [Vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

### Step 3: Configure Environment Variables
In Vercel dashboard, add:
```
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app/api
```

### Step 4: Deploy
Click "Deploy" - Vercel will build and deploy automatically!

---

## Post-Deployment Checklist

### Backend (Railway)
- [ ] Test API endpoint: `https://your-backend.railway.app/docs`
- [ ] Verify CORS allows Vercel domain
- [ ] Check logs for any errors
- [ ] Test file upload endpoint

### Frontend (Vercel)
- [ ] Test website loads correctly
- [ ] Verify API calls work (check browser console)
- [ ] Test file upload functionality
- [ ] Check CORS errors in console

### CORS Configuration
If you get CORS errors, update `backend/main.py`:
```python
# Replace "*" with your Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## Troubleshooting

### Backend Issues
- **Port Error**: Railway provides `$PORT` env var automatically
- **Playwright Error**: Make sure `playwright install chromium` runs in build
- **Memory Issues**: Railway free tier has limits, upgrade if needed

### Frontend Issues
- **API Connection**: Check `NEXT_PUBLIC_API_URL` is correct
- **Build Errors**: Check Vercel build logs
- **CORS Errors**: Update backend CORS settings

---

## Environment Variables Summary

### Backend (Railway)
```
OPENAI_API_KEY=sk-...
PORT=8000 (auto-set by Railway)
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
```

---

## Notes
- Railway provides persistent storage for `runs/` directory
- Vercel has file size limits (100MB for serverless functions)
- Consider using S3 for file storage if needed
- Monitor Railway usage (free tier has limits)

