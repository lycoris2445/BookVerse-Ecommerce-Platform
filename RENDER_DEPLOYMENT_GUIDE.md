#  Render.com Deployment Guide

##  Pre-deployment Checklist
-  PostgreSQL database configured
-  Static files collection setup
-  Environment variables template ready
-  PayPal integration configured

##  Render Setup Steps

### 1. Create New Web Service
1. Go to https://dashboard.render.com
2. Click 'New'  'Web Service'
3. Connect your GitHub repository: **BookVerse-Ecommerce-Platform**
4. Configure:
   - **Name**: bookverse-backend
   - **Environment**: Python 3
   - **Build Command**: \./backend/build.sh\
   - **Start Command**: \gunicorn config.wsgi:application --bind 0.0.0.0:\\
   - **Root Directory**: \ackend\

### 2. Environment Variables
Add these in Render Dashboard  Environment tab:

\\\
# Django Core
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-here-minimum-50-chars
DEBUG=False

# PayPal Configuration (Sandbox)
PAYPAL_CLIENT_ID=AQ3aier7n8biTEQWSB-457vXd23i_bgPftxf15QgKKzuco2VpSoG1yLdfCE4NKm9ppb4j_T7NoKxwQJL
PAYPAL_CLIENT_SECRET=your-paypal-client-secret-from-dashboard
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_SANDBOX=True

# URLs (Update with your actual domain)
BACKEND_URL=https://bookverse-backend.onrender.com
FRONTEND_URL=https://bookverse-frontend.vercel.app
ALLOWED_HOSTS=bookverse-backend.onrender.com,localhost,127.0.0.1
\\\

### 3. Database Setup
1. In Render Dashboard  Create 'PostgreSQL' service
2. Copy the **Internal Database URL**
3. Add to Environment Variables:
   - **DATABASE_URL**: \postgresql://username:password@host:port/database\

### 4. PayPal Webhook Configuration
After deployment, configure webhook in PayPal Developer Dashboard:
- **Webhook URL**: \https://bookverse-backend.onrender.com/api/v1/payments/paypal/webhook/\
- **Events**: 
  - PAYMENT.CAPTURE.COMPLETED
  - PAYMENT.CAPTURE.DENIED

##  Testing Endpoints

After successful deployment, test these URLs:

### Health Check
- \GET https://bookverse-backend.onrender.com/admin/\

### API Endpoints  
- \GET https://bookverse-backend.onrender.com/api/v1/catalog/products/\
- \GET https://bookverse-backend.onrender.com/api/v1/recommendations/popular/\

### PayPal Integration
- \POST https://bookverse-backend.onrender.com/api/v1/payments/paypal/create-order/\
- \POST https://bookverse-backend.onrender.com/api/v1/payments/paypal/webhook/\

##  Troubleshooting

### Common Issues:
1. **Build fails**: Check build.sh permissions and Python version
2. **Database connection**: Verify DATABASE_URL format
3. **Static files 404**: Ensure collectstatic runs in build.sh
4. **PayPal errors**: Check CLIENT_ID and webhook URL

### Debug Commands:
\\\ash
# Check logs in Render Dashboard
# Or use Render CLI
render logs --service=bookverse-backend
\\\

##  Performance Optimization
- Enable auto-deploy from GitHub
- Set up health checks: \/admin/\
- Configure alerts for downtime
- Monitor resource usage

---
 **Deployment Ready!** Your BookVerse platform should be live and accessible.

