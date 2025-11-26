# Testing Guide for AI Course Quiz System

## Prerequisites Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up MongoDB Atlas (Free Tier)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account and cluster
3. Click "Connect" → "Connect your application"
4. Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
5. Replace `<password>` with your actual password
6. Add `/quiz_ai_db` before the `?` to specify the database name

### 3. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create or get your API key
3. Copy the key (starts with `AIza...`)

### 4. Set Environment Variables
```bash
export GEMINI_API_KEY="AIzaSyCQoU--QK_PSjI2DgWGSMrzheP9yZsLi4I"
export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/quiz_ai_db?retryWrites=true&w=majority"
```

Or create a `.env` file and source it:
```bash
cp .env.example .env
# Edit .env with your actual values
source .env
```

---

## Running the App

### Start the Streamlit Server
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Testing Workflow

### Test 1: Basic Quiz Generation
1. **Enter a nickname**: e.g., "TestUser1"
2. **Enter topics**: e.g., "encryption, hashing"
3. **Select difficulty**: Choose "medium"
4. **Click "Start Quiz"**
   - ✅ Expected: Spinner shows "Generating or retrieving quiz..."
   - ✅ Expected: Success message "Quiz ready. Scroll down to take it."
   - ✅ Expected: 5 multiple-choice questions appear below

### Test 2: Taking the Quiz
1. **Select answers** for each question (click radio buttons)
2. **Click "Submit Quiz"**
   - ✅ Expected: Score displayed (e.g., "You scored 3 / 5 (60.0%)")
   - ✅ Expected: Page refreshes and shows "Review Quiz" section

### Test 3: Review Answers
1. **Scroll to "Review Quiz" section**
   - ✅ Expected: All questions shown with:
     - ✅ Green checkmark on correct answers
     - ❌ Red X on your incorrect selections
     - Explanation/reference for each question

### Test 4: Quiz Caching (MongoDB Storage)
1. **Keep the same nickname and topics**
2. **Click "Start Quiz" again**
   - ✅ Expected: Same quiz loads instantly (no AI generation)
   - ✅ Expected: Message confirms quiz retrieval

### Test 5: Different User/Topics
1. **Change nickname** to "TestUser2" or **change topics** to "firewalls, VPN"
2. **Click "Start Quiz"**
   - ✅ Expected: New quiz generated with different questions

### Test 6: Load Existing Quiz
1. **Enter a nickname** you used before
2. **Click "Load Existing Quiz"**
   - ✅ Expected: Previous quiz loads
   - ✅ Expected: Can retake the same quiz

### Test 7: Score History (Sidebar)
1. **In the sidebar**, enter a nickname in "Lookup nickname"
2. **Click "Show history"**
   - ✅ Expected: List of past scores with timestamps
   - ✅ Expected: Format: `2025-11-12 15:30:45: 4 / 5 (80.0%)`

### Test 8: Different Difficulty Levels
1. Try each difficulty: "easy", "medium", "hard"
   - ✅ Expected: Questions reflect difficulty level
   - ✅ Expected: Each combination creates a separate quiz in DB

---

## Troubleshooting

### Error: "GEMINI_API_KEY is not set"
**Solution**: Export the environment variable before running:
```bash
export GEMINI_API_KEY="your_actual_key"
```

### Error: "MongoDB connection error"
**Solution**: Check your `MONGO_URI`:
- Ensure username/password are correct (no special chars without encoding)
- Whitelist your IP in MongoDB Atlas Network Access
- Test connection: `mongosh "your_connection_string"`

### Error: "No .txt files found in the data/ folder"
**Solution**: Check that `data/day1.txt`, `data/day2.txt`, etc. exist:
```bash
ls -la data/
```

### Error: "AI generation failed" or "Failed to parse JSON"
**Possible causes**:
1. **Invalid API key** - verify key is correct (must start with "AIza...")
2. **API rate limit** - wait and try again, or check your quota
3. **Model response format** - Gemini might wrap JSON in markdown code blocks

**Solutions**:
- Verify your `GEMINI_API_KEY` at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check API quota and usage limits
- The app has robust JSON extraction (strips markdown code blocks automatically)
- Try with simpler topics if generation consistently fails

### Quiz Questions Look Wrong
**Solution**: 
- Check that `.txt` files in `data/` contain relevant course content
- Try different topics that match your content
- Increase context by adding more text to the corpus

---

## Verification Checklist

- [ ] App starts without errors
- [ ] MongoDB connection successful
- [ ] Quiz generates with AI
- [ ] Questions display correctly
- [ ] Can select answers
- [ ] Score calculates correctly
- [ ] Review shows correct/incorrect answers
- [ ] Explanations appear
- [ ] Same user gets cached quiz
- [ ] Score history displays in sidebar
- [ ] Different difficulties create different quizzes

---

## Sample Test Data

### Good Test Topics
Based on the sample data in `data/`:
- "cryptography, encryption"
- "network security, firewalls"
- "authentication, access control"
- "cybersecurity, threats"
- "hashing, SHA-256"

### Expected Behavior
- **Easy**: More straightforward, definition-based questions
- **Medium**: Mix of concepts and application
- **Hard**: Complex scenarios, deep understanding required

---

## MongoDB Verification

Check data was stored in MongoDB:

### Using MongoDB Compass (GUI)
1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect with your `MONGO_URI`
3. Navigate to `quiz_ai_db` database
4. Check collections:
   - `quizzes` - stored generated quizzes
   - `scores` - user scores and attempts

### Using mongosh (CLI)
```bash
mongosh "your_mongo_uri"

use quiz_ai_db
db.quizzes.find().pretty()
db.scores.find().pretty()
```

---

## Performance Notes

- **First quiz generation**: 5-15 seconds (AI call)
- **Cached quiz retrieval**: < 1 second (MongoDB query)
- **Score calculation**: Instant (local computation)
- **Review display**: Instant (from session state)

---

## Azure Deployment Testing

After deploying to Azure App Service:

1. **Set environment variables** in Azure Portal:
   - Configuration → Application settings → New application setting
   - Add `GEMINI_API_KEY` and `MONGO_URI`

2. **Test the deployed URL**: `https://your-app.azurewebsites.net`

3. **Check logs** in Azure Portal:
   - Log stream for real-time debugging
   - Application Insights for metrics

---

## Next Steps

1. ✅ Run basic tests above
2. 🔧 If `google_adk` import fails, update to correct package/API
3. 📊 Verify data in MongoDB
4. 🚀 Deploy to Azure and test in production
5. 🎨 Customize UI/styling if needed
