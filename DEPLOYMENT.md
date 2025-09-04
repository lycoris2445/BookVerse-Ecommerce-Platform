# BookVerse Deployment Guide

## 🚀 Deploy Backend to Render

### Step 1: Prepare Your Repository
1. Make sure all files are committed to your GitHub repository
2. Push the latest changes: `git push origin main`

### Step 2: Create Render Account & Service
1. Go to [render.com](https://render.com) and sign up/login
2. Connect your GitHub account
3. Click "New" → "Web Service"
4. Select your repository: `DacienNguyeen/EcomTech`
5. Configure the service:
   - **Name**: `bookverse-backend` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
   - **Root Directory**: `backend`

### Step 3: Add Environment Variables in Render
Go to your service → Environment tab and add:

```
SECRET_KEY=your-very-long-secret-key-here-generate-a-new-one
DJANGO_SETTINGS_MODULE=config.settings.production

# CloudMonster ASP MySQL Database
DB_NAME=your_database_name
DB_USER=your_database_user  
DB_PASSWORD=your_database_password
DB_HOST=your_cloudmonster_mysql_host
DB_PORT=3306
```

### Step 4: Database Setup
Since you're using CloudMonster ASP MySQL:
1. Get your MySQL connection details from CloudMonster ASP dashboard
2. Add the database environment variables to Render (as shown above)
3. The Django app will connect to your existing MySQL database
4. Run migrations after first deployment (check Render logs)

### Step 5: Update ALLOWED_HOSTS
After deployment, update `backend/config/settings/production.py`:
```python
ALLOWED_HOSTS = [
    'your-actual-app-name.onrender.com',  # Replace with actual Render URL
    'localhost',
    '127.0.0.1',
]
```

---

## 🌐 Deploy Frontend to Vercel

### Step 1: Prepare Vercel Account
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Connect your GitHub account

### Step 2: Deploy from GitHub
1. Click "Add New..." → "Project"
2. Import your repository: `DacienNguyeen/EcomTech`
3. Configure project:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - Click "Deploy"

### Step 3: Add Environment Variables in Vercel
1. Go to Project Settings → Environment Variables
2. Add:
   ```
   REACT_APP_API_URL = https://your-backend-name.onrender.com
   ```
3. Redeploy to apply changes

### Step 4: Update Backend CORS
After frontend is deployed, update `backend/config/settings/production.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-name.vercel.app",  # Replace with actual Vercel URL
    "http://localhost:3000",
]
```

---

## 🔧 Production URLs

After deployment, your URLs will be:
- **Backend**: `https://your-backend-name.onrender.com`
- **Frontend**: `https://your-frontend-name.vercel.app`

## 🛠️ Troubleshooting

### Backend Issues:
- Check Render logs for build/runtime errors
- Verify environment variables are set correctly
- Make sure DATABASE_URL is configured if using PostgreSQL

### Frontend Issues:
- Verify REACT_APP_API_URL points to correct backend URL
- Check Network tab in browser for API call errors
- Ensure CORS is configured correctly in backend

### Database:
- Configure CloudMonster ASP MySQL connection details in environment variables
- Make sure your CloudMonster MySQL allows connections from Render servers
- Verify DB_HOST, DB_USER, DB_PASSWORD, DB_NAME are correct

---

## 📝 Post-Deployment Checklist

- [ ] Backend deployed successfully on Render
- [ ] Frontend deployed successfully on Vercel  
- [ ] Environment variables configured
- [ ] Database connected and migrated
- [ ] CORS configured for frontend domain
- [ ] Test all main features (catalog, recommendations, cart)
- [ ] Test activity tracking
- [ ] Verify image loading works
