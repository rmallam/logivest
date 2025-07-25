# Render Deployment Guide for Real Estate Investment Analyzer

## Progressive Build Strategy
This application uses a robust multi-stage build process to ensure deployment success:

1. **Primary Build**: Full feature set with Gemini AI support (`requirements.txt`)
2. **Fallback Build**: Core functionality if AI packages fail (`requirements-minimal.txt`)
3. **Graceful Degradation**: App works even without AI features

## Features Available
- ✅ Complete real estate calculation engine
- ✅ Rent-to-EMI analysis for Australian market
- ✅ Responsive web interface 
- ✅ Property valuation tools
- ⚠️ Gemini AI insights (environment dependent)

## Setting up Gemini API Key as Secret File in Render

### 1. Prepare your API key file locally:

1. Edit the `gemini_api_key.txt` file in your project root
2. Replace `your-actual-gemini-api-key-here` with your real Gemini API key
3. **DO NOT commit this file to git** (it's already in .gitignore)

2. **Deploy to Render with Multi-Stage Build**:

1. **Create Web Service** in Render Dashboard:
   - Connect your GitHub repository: `rmallam/logivest`
   - **Environment**: Python 3
   - **Build Command**: *Leave blank* (uses render.yaml configuration)
   - **Start Command**: *Leave blank* (uses render.yaml configuration)

2. **Advanced Build Process** (handled automatically):
   - Primary attempt: Install all packages including Gemini AI
   - Fallback: Use minimal requirements if AI packages fail
   - Result: App deploys successfully regardless of package availability

2. **Add Secret Files** in Render:
   - Go to your service dashboard
   - Navigate to **Environment** tab
   - Scroll down to **Secret Files** section
   - Click **Add Secret File**
   - **Filename**: `gemini_api_key.txt`
   - **File Contents**: Paste your actual Gemini API key (just the key, no comments)

### 3. Environment Variables (Optional):
If you prefer environment variables instead, set:
- `GEMINI_API_KEY` = `your-actual-api-key`

### 4. The code will automatically:
- First try to read from `GEMINI_API_KEY` environment variable
- If not found, try to read from `gemini_api_key.txt` secret file
- If neither is available, AI features will be disabled (app still works)

### 5. Security Benefits:
- API key is not stored in your git repository
- Secret files are encrypted at rest in Render
- No risk of accidentally exposing the key in code

### 6. Local Development:
For local development, you can either:
- Set environment variable: `export GEMINI_API_KEY=your-key`
- Or create local `gemini_api_key.txt` file (git ignored)

## Troubleshooting Build Issues

### If Deployment Fails:
1. **Check Build Logs**: Look for specific package installation errors
2. **Fallback Option**: Manually set build command to `pip install -r requirements-minimal.txt`
3. **AI Features**: App will automatically disable AI if packages unavailable

### Manual Fallback Deployment:
If automatic build fails, override in Render dashboard:
- **Build Command**: `pip install -r requirements-minimal.txt`
- **Start Command**: `python web_interface/app.py`

### Testing Locally:
```bash
# Test full build
pip install -r requirements.txt
python web_interface/app.py

# Test minimal build  
pip install -r requirements-minimal.txt
python web_interface/app.py
```

Visit http://localhost:5001 to verify functionality.

## Example Secret File Content:
```
AIzaSyC-your-actual-gemini-api-key-here-32-characters
```

That's it! Your Gemini API key will be securely loaded in production. 🔐
