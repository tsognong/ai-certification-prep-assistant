# Quiz AI Agent

AI-powered quiz generation system using Google Gemini and MongoDB Atlas.

## Features

- 🤖 **AI-Generated Quizzes** - Uses Google Gemini to create custom quizzes from course materials or custom topics
- 📚 **Course Materials** - Reads text files from `./data/*.txt` and combines them as context
- 💾 **MongoDB Integration** - Stores quizzes, scores, and user data in MongoDB Atlas
- 🔒 **Browser Fingerprinting** - Prevents API limit bypass using FingerprintJS
- 🎯 **Custom Topics** - Users can type custom topics in addition to predefined options
- 📊 **Score Tracking** - View recent quiz scores in the sidebar
- ☁️ **Azure Deployment** - Ready to deploy to Azure App Service

## Quick Start

1. Create a Python virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables:

```bash
export GEMINI_API_KEY="your_gemini_key_here"
export MONGO_URI="your_mongodb_connection_uri_here"
```

Or create a `.env` file (see `.env.example`).

4. Make sure `./data/` exists and contains one or more `.txt` files (e.g., `day1.txt`, `day2.txt`).

5. **(Optional but recommended)** Verify your setup:

```bash
python test_setup.py
```

6. Run the app:

```bash
streamlit run app.py
```

7. **Test the app** - See [TESTING.md](TESTING.md) for detailed testing workflows

## Deployment

### Azure App Service

Deploy to Azure using the provided scripts:

```bash
./deploy.sh  # Initial deployment
./update.sh  # Quick updates
./status.sh  # Check deployment status
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Security

- ✅ Error handling hides stack traces and credentials from users
- ✅ Browser fingerprinting prevents API limit abuse
- ✅ Environment variables stored securely in Azure App Settings
- ✅ See [SECURITY.md](SECURITY.md) for security best practices

## Files

- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `data/` - Course text files directory
- `deploy.sh` - Azure deployment script
- `update.sh` - Quick update deployment
- `status.sh` - Deployment status checker
- `.streamlit/config.toml` - Streamlit configuration
