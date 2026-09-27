# Deployment Guide

Deploy your app to the cloud for free in 30 minutes.

## Stack

- **Backend** → Render (free tier)
- **Frontend** → Vercel (free tier)
- **Database** → Supabase (already set up ✓)

## Prerequisites

1. GitHub account
2. Render account (render.com)
3. Vercel account (vercel.com)

## Step 1: Push to GitHub (5 min)

```bash
cd "C:\Users\Sanju\OneDrive\Desktop\Apps n Extensions\HOPE-Elite\HDP 1-Agentic AI\AgenticAI-Project\socratic-tutoring-system"

# Initialize git (if not done)
git init
git add .
git commit -m "Ready for deployment"

# Create repo on GitHub then:
git remote add origin https://github.com/YOUR_USERNAME/socratic-tutoring-system.git
git push -u origin main
```

## Step 2: Deploy Backend to Render (10 min)

1. Go to **render.com** → Sign up/Login
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub → Select your repository
4. Configure:
   - **Name:** socratic-tutor-api
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.api.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

5. Add **Environment Variables:**
   - `GROQ_API_KEY` = `your_groq_api_key_here`
   - `DATABASE_URL` = `your_supabase_database_url_here`

6. Click **"Create Web Service"**
7. **Save your URL:** `https://socratic-tutor-api-XXXX.onrender.com`

## Step 3: Deploy Frontend to Vercel (10 min)

1. Go to **vercel.com** → Sign up/Login with GitHub
2. Click **"New Project"**
3. Select your repository
4. Configure:
   - **Framework:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

5. Add **Environment Variable:**
   - Key: `VITE_API_URL`
   - Value: Your Render URL (from Step 2)

6. Click **"Deploy"**
7. **Save your URL:** `https://your-app.vercel.app`

## Step 4: Test (5 min)

1. Open your Vercel URL
2. Login with student ID
3. Select a problem → Start session
4. Type an answer → Tutor responds!

## Important Notes

### Render Free Tier
- Sleeps after 15 min of inactivity
- First request takes 30-60 seconds to wake up
- Then it's fast!

### Cost
Everything is **100% FREE**:
- Render: 750 hours/month
- Vercel: 100 GB bandwidth/month
- Supabase: 500 MB database

## Updating Your App

After making changes:
```bash
git add .
git commit -m "Your changes"
git push
```

Both Render and Vercel auto-deploy in 2-5 minutes!

## Troubleshooting

**Backend not responding?**
- Check Render logs
- Verify environment variables
- Wait 60 seconds (might be waking up)

**Frontend can't reach backend?**
- Check `VITE_API_URL` in Vercel settings
- Make sure it's your Render URL

**Database errors?**
- Verify `DATABASE_URL` starts with `postgresql://`
- Check Supabase is accessible

## Your Live URLs

After deployment:

- **Live App:** https://_______________.vercel.app
- **Backend API:** https://_______________.onrender.com
- **Database:** Supabase (already deployed)

Share the live app URL with anyone - no installation needed!
