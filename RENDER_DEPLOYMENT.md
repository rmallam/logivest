# Render Secret File Deployment Guide

## Setting up Gemini API Key as Secret File in Render

### 1. Prepare your API key file locally:

1. Edit the `gemini_api_key.txt` file in your project root
2. Replace `your-actual-gemini-api-key-here` with your real Gemini API key
3. **DO NOT commit this file to git** (it's already in .gitignore)

### 2. Deploy to Render with Secret File:

1. **Create Web Service** in Render Dashboard:
   - Connect your GitHub repository: `rmallam/logivest`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_interface/app.py`

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

## Example Secret File Content:
```
AIzaSyC-your-actual-gemini-api-key-here-32-characters
```

That's it! Your Gemini API key will be securely loaded in production. 🔐
