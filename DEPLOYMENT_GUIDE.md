# 🚀 Streamlit Cloud Deployment Guide

Complete step-by-step guide to deploy your FHIR IPS Validator to Streamlit Community Cloud (FREE).

---

## 📋 Prerequisites

✅ **You already have these:**
- [x] GitHub repository: https://github.com/ddeveloper72/fhir-ips-validator
- [x] Code pushed to GitHub
- [x] `requirements.txt` file
- [x] Public repository (required for free tier)

✅ **You'll need:**
- [ ] GitHub account (you have this)
- [ ] API keys ready to copy from your `.env` file

---

## 🎯 Step-by-Step Deployment

### Step 1: Go to Streamlit Cloud

1. Open your browser and go to: **https://share.streamlit.io**
2. Click **"Sign up"** (top right)
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub account

---

### Step 2: Create New App

1. Once logged in, click the **"New app"** button (big blue button)
2. You'll see a form with three fields:

   **Repository:** Select `ddeveloper72/fhir-ips-validator`
   
   **Branch:** `main`
   
   **Main file path:** `streamlit_app.py`

3. Click **"Advanced settings..."** (optional, we'll add secrets in a moment)

---

### Step 3: Add Your Secrets

This is the **most important step** - your app needs API keys to work!

1. **Option A - During Initial Setup:**
   - In the "Advanced settings" section, you'll see "Secrets"
   - Copy and paste your secrets (see format below)

2. **Option B - After Deployment:**
   - Click on your app in the dashboard
   - Click the **⚙️ Settings** icon
   - Go to **"Secrets"** tab
   - Paste your secrets there

**Secrets Format** (copy from your `.env` file):

```toml
# eHDSI Gazelle API Configuration
EVS_API_KEY = "JXw21yMdi8aT1dP5PKuJNwzjRX3kkiAWRgUhF4jty8HsN17oyuJVi2ZhT6aWxQj7iT7Inj9yPApoF80lRDKBkZw1K3c6poLXrHsx46D1Nn3HKjz1ibyVZrkDpl3tRAiF"
EVS_API_KEY_CREATION_DATE = "5/16/26 12:17:02 PM (CEST GMT+0200)"
EVS_API_KEY_EXPIRY_DATE = "6/15/26"
EVS_BASE_URL = "https://gazelle.ehdsi.eu"

# EHDS Gazelle API Configuration
EHDS_GAZELLE_API_KEY = "your_ehds_gazelle_api_key_here"
EHDS_GAZELLE_API_KEY_CREATION_DATE = "5/16/26 2:20:19 PM (CEST GMT+0200)"
EHDS_GAZELLE_API_KEY_EXPIRY_DATE = "6/16/26"
EHDS_GAZELLE_BASE_URL = "https://ehds.gazelle-platform.net"

# Azure FHIR Service Configuration
AZURE_FHIR_URL = "https://healtthdata-dev-fhir-service.fhir.azurehealthcareapis.com"
AZURE_CLIENT_ID = "47758bef-c9fa-419d-a752-6353a1089305"
AZURE_CLIENT_SECRET = "your_azure_client_secret_here"
AZURE_TENANT_ID = "your_azure_tenant_id_here"
```

⚠️ **IMPORTANT:** Replace the placeholder values with your actual credentials from your `.env` file!

---

### Step 4: Deploy!

1. Click **"Deploy!"** button
2. Wait 2-5 minutes while Streamlit:
   - Installs Python dependencies
   - Sets up the environment
   - Starts your app

You'll see a build log showing progress:
```
[...]
Successfully installed streamlit-1.32.0 zeep-4.2.1 ...
[...]
```

---

### Step 5: Your App is Live! 🎉

Once deployed, you'll get a URL like:
```
https://fhir-ips-validator.streamlit.app
```

Or possibly:
```
https://ddeveloper72-fhir-ips-validator-streamlit-app.streamlit.app
```

**Test it:**
- Upload a FHIR bundle (Patrick Murphy example)
- Try validating with Azure FHIR
- Test CDA validation with Gazelle
- Check FHIR IPS validation with Matchbox

---

## 🔄 Automatic Updates

**Best part:** Every time you push to GitHub, your app automatically redeploys!

```powershell
# Make changes locally
git add .
git commit -m "feat: add new feature"
git push

# Streamlit Cloud automatically detects the push and redeploys
# Wait ~2 minutes and your changes are live!
```

---

## ⚙️ App Settings & Management

### Access Settings:
1. Go to https://share.streamlit.io
2. Click on your app
3. Click ⚙️ **Settings**

### Available Options:

**General:**
- App URL (can customize subdomain)
- App name
- Description
- Delete app

**Secrets:**
- Add/edit environment variables
- Encrypted at rest
- Never shown in logs

**Sharing:**
- Make app public (default for free tier)
- Share link with others

**Resources:**
- View CPU/memory usage
- Check deployment history
- See logs

**Reboot:**
- Force restart if app is stuck
- Clear cache

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Check `requirements.txt` has all dependencies
```powershell
# Locally test your requirements.txt
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Issue: "Secrets not found"
**Solution:** Verify secrets are added in Streamlit Cloud dashboard
- Settings → Secrets → Paste secrets → Save

### Issue: App keeps crashing
**Solution:** Check logs in Streamlit Cloud
- Click on app → "Manage app" → View logs
- Look for Python errors

### Issue: "This app has gone to sleep"
**Solution:** This is normal for free tier
- App sleeps after 7 days of inactivity
- Wakes up automatically when someone visits (30 seconds)
- Or click "Wake up" button

### Issue: Slow performance
**Solution:** Free tier has limited resources
- 1 GB RAM (shared)
- Optimize code to reduce memory usage
- Consider caching with `@st.cache_data`

---

## 📊 What's Included in Free Tier

| Feature | Free Tier | Details |
|---------|-----------|---------|
| **Apps** | Unlimited | Deploy as many as you want |
| **Resources** | 1 GB RAM | Shared across apps |
| **Storage** | Limited | For app files only |
| **Compute** | Unlimited | No time limits! |
| **Auto-deploys** | ✅ Yes | From Git commits |
| **Custom domain** | ❌ No | Use *.streamlit.app subdomain |
| **Private apps** | ❌ No | Public only on free tier |
| **Support** | Community | Forum support only |

---

## 🔒 Security Best Practices

### ✅ DO:
- Keep secrets in Streamlit Cloud dashboard only
- Use environment variables for all credentials
- Monitor app access logs
- Rotate API keys regularly (before expiry dates)

### ❌ DON'T:
- Never commit secrets to GitHub
- Don't log sensitive data
- Don't expose credentials in error messages
- Don't share your `.env` file

---

## 📈 Monitoring Your App

### View App Analytics:
1. Go to https://share.streamlit.io
2. Click on your app
3. View metrics:
   - Visitor count
   - Resource usage (CPU/RAM)
   - Deployment history
   - Error logs

### Check Logs:
```
Settings → Logs → View real-time logs
```

Logs show:
- App startup
- User interactions
- Errors and warnings
- API calls (without secrets)

---

## 🚀 Post-Deployment Checklist

After successful deployment:

- [ ] Test all three validators (Azure FHIR, EHDS Matchbox, Gazelle EVS)
- [ ] Upload example files (Patrick Murphy bundle, Diana Ferreira CDA)
- [ ] Verify platform switching (eHDSI vs EHDS Gazelle)
- [ ] Test validation mode selector (strict vs permissive)
- [ ] Check auto-detection of CDA document types
- [ ] Verify all error messages display correctly
- [ ] Test with real-world documents
- [ ] Share URL with colleagues for feedback
- [ ] Add app URL to your README.md
- [ ] Set up monitoring alerts (if needed)

---

## 🆘 Getting Help

**Streamlit Community Forum:**
https://discuss.streamlit.io

**Common Issues:**
https://docs.streamlit.io/streamlit-community-cloud/troubleshooting

**Documentation:**
https://docs.streamlit.io/streamlit-community-cloud

**Your GitHub Issues:**
https://github.com/ddeveloper72/fhir-ips-validator/issues

---

## 🎓 Next Steps

Once your app is live:

1. **Share it!** 
   - Add badge to README.md
   - Share on LinkedIn/Twitter
   - Demo to colleagues

2. **Monitor usage**
   - Check analytics dashboard
   - Review error logs
   - Gather user feedback

3. **Iterate**
   - Fix bugs
   - Add features
   - Push to GitHub (auto-deploys!)

4. **Consider upgrading**
   - Streamlit Cloud Pro ($20/month)
   - Private apps
   - More resources
   - Priority support

---

## 📝 Quick Reference Card

```
┌─────────────────────────────────────────────┐
│  STREAMLIT CLOUD DEPLOYMENT CHEAT SHEET     │
├─────────────────────────────────────────────┤
│                                             │
│  🌐 Dashboard:                              │
│     https://share.streamlit.io              │
│                                             │
│  📦 Your App URL (after deployment):        │
│     https://fhir-ips-validator.streamlit... │
│                                             │
│  🔑 Add Secrets:                            │
│     Settings → Secrets → Paste → Save       │
│                                             │
│  🔄 Redeploy:                               │
│     Just push to GitHub!                    │
│                                             │
│  🐛 View Logs:                              │
│     Click app → Manage app → Logs           │
│                                             │
│  ⚡ Reboot App:                             │
│     Settings → Reboot                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## ✅ You're Ready!

Follow the steps above and you'll have your app live in **less than 10 minutes**! 🎉

**Any issues?** Check the troubleshooting section or ask me for help!
