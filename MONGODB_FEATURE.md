# MongoDB Developer Associate Exam Feature

## Overview
Extended the Quiz AI Agent application to support two quiz types:
1. **AI Agent Course** (existing functionality)
2. **MongoDB Developer Associate Exam** (new feature)

## Implementation Summary

### New Modules Created

#### 1. `mongo_fetcher.py`
**Purpose:** Fetch MongoDB documentation from mongodb.com/docs in real-time

**Key Functions:**
- `fetch_mongo_doc(url)` - Scrapes MongoDB documentation pages
- `fetch_docs_for_topics(topics, max_pages_per_topic=2)` - Fetches docs for selected topics
- `format_docs_for_context(docs)` - Formats docs for LLM context
- `get_available_mongo_topics()` - Returns list of 10 exam topics

**Topics Covered:**
1. CRUD Operations
2. Aggregation Framework
3. Indexes
4. Data Modeling
5. Transactions
6. Replication
7. Sharding
8. MongoDB Drivers
9. Security
10. Performance

**Documentation URLs:** ~30 mapped URLs covering all exam domains

#### 2. `exam_loader.py`
**Purpose:** Parse MongoDB exam guide and extract requirements

**Key Functions:**
- `load_exam_guide()` - Loads exam guide from data/mongo/mongo-developer-exam-guide.txt
- `extract_topics_from_guide()` - Extracts exam topics from guide
- `extract_requirements()` - Returns question distribution (60% MCQ, 40% MSQ)

**Requirements:**
- MCQ: 1 correct answer + 3 distractors
- MSQ: 2-3 correct answers + 2-4 distractors
- Difficulty levels: easy, medium, hard

#### 3. `mongo_question_generator.py`
**Purpose:** Generate and grade MongoDB exam-style questions

**Key Functions:**
- `create_mongo_question_prompt()` - Creates detailed LLM prompt with documentation context
- `validate_mongo_questions()` - Validates question structure and answer format
- `grade_mongo_quiz()` - Grades both MCQ and MSQ questions

**Question Structure:**
```json
{
  "type": "mcq" | "msq",
  "question": "Question text",
  "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
  "correct_answers": [0, 2],  // Array for both types
  "explanation": "Explanation text",
  "sources": ["https://docs.mongodb.com/..."]
}
```

**Grading Logic:**
- **MCQ:** Exact match of single answer
- **MSQ:** Exact set equality (must select ALL correct answers, no more, no less)

### Modified Files

#### 1. `requirements.txt`
Added dependencies:
- `requests` - HTTP library for fetching web pages
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

#### 2. `app.py`
**Major Changes:**

**Imports:**
```python
from mongo_fetcher import fetch_docs_for_topics, get_available_mongo_topics, format_docs_for_context
from exam_loader import load_exam_guide, extract_topics_from_guide, extract_requirements
from mongo_question_generator import create_mongo_question_prompt, validate_mongo_questions, grade_mongo_quiz
```

**Constants:**
```python
MONGO_EXAM_GUIDE = Path("data/mongo/mongo-developer-exam-guide.txt")
QUIZ_TYPE_AI_COURSE = "AI Agent Course"
QUIZ_TYPE_MONGO_EXAM = "MongoDB Developer Associate Exam"
```

**New Function:**
- `generate_mongo_quiz_with_ai()` - Generates MongoDB exam questions using:
  - Fetches documentation for selected topics
  - Formats docs as context
  - Loads exam requirements
  - Creates prompt with documentation context
  - Uses Google Gemini to generate questions
  - Validates questions (MCQ: 1 answer, MSQ: 2-3 answers)
  - Returns validated questions list

**Modified Functions:**
- `get_quiz_key()` - Now includes `quiz_type` parameter
- `get_or_create_quiz()` - Added `quiz_type` parameter, conditionally generates AI or MongoDB quiz
- `main()` - Complete UI overhaul:
  - Added quiz type dropdown selector
  - Conditional topic selection (AI topics vs MongoDB topics)
  - Dual question rendering:
    - `st.radio()` for MCQ (single choice)
    - `st.multiselect()` for MSQ (multiple choice)
  - Conditional grading:
    - `calculate_score()` for AI course
    - `grade_mongo_quiz()` for MongoDB exam
  - Enhanced review section:
    - Shows MSQ indicator
    - Displays list of correct answers for MSQ
    - Shows documentation sources for MongoDB questions

**UI Flow:**
1. User selects quiz type (dropdown)
2. Topics shown based on type:
   - AI Course: Existing AVAILABLE_TOPICS + custom input
   - MongoDB Exam: 10 exam topics from MONGO_DOC_URLS
3. Select difficulty (easy/medium/hard)
4. Start quiz or load recent quiz
5. Question navigation:
   - MCQ: Checkboxes with "Select ONE answer" hint
   - MSQ: Checkboxes with "Select ALL that apply" hint
6. Submit quiz
7. Review with:
   - Question-by-question breakdown
   - Correct/incorrect indicators
   - Explanations
   - Documentation sources (MongoDB only)

## Database Schema Updates

### `quizzes` Collection
Added field:
- `quiz_type`: "AI Agent Course" | "MongoDB Developer Associate Exam"

Updated query logic to include `quiz_type` in find operations.

## Key Features

### 1. Real-Time Documentation Fetching
- No local HTML storage
- Fetches from mongodb.com/docs during quiz generation
- Uses BeautifulSoup for robust HTML parsing
- Handles rate limiting and errors gracefully

### 2. Dual Question Types
- **MCQ (Multiple Choice Question):** 1 correct answer
- **MSQ (Multiple Select Question):** 2-3 correct answers
- Visual indicators for each type
- Separate rendering and grading logic

### 3. MongoDB-Specific Grading
- MCQ: Direct equality check
- MSQ: Set equality (order doesn't matter)
- Feedback includes:
  - Your answers vs correct answers
  - Explanation
  - Documentation URLs

### 4. Modular Architecture
- Separate modules for fetching, loading, generating
- Clean separation of concerns
- Easy to extend with additional quiz types

## Testing

### Syntax Validation
All modules compile successfully:
```bash
python3 -m py_compile app.py
python3 -m py_compile mongo_fetcher.py
python3 -m py_compile exam_loader.py
python3 -m py_compile mongo_question_generator.py
```

### Application Launch
```bash
streamlit run app.py --server.port 8501
```
✅ Application starts without errors
✅ URL: http://0.0.0.0:8501

## File Structure
```
quiz-ai-agent/
├── app.py (MODIFIED)
├── mongo_fetcher.py (NEW)
├── exam_loader.py (NEW)
├── mongo_question_generator.py (NEW)
├── requirements.txt (MODIFIED)
├── data/
│   ├── ai/
│   │   ├── day1.txt
│   │   ├── day2.txt
│   │   ├── day3.txt
│   │   └── Day4.txt
│   └── mongo/
│       └── mongo-developer-exam-guide.txt
└── MONGODB_FEATURE.md (NEW - this file)
```

## Next Steps

### For Testing:
1. Start the app: `streamlit run app.py`
2. Select "MongoDB Developer Associate Exam" from dropdown
3. Choose topics (e.g., CRUD Operations, Aggregation)
4. Select difficulty
5. Generate quiz
6. Test both MCQ and MSQ questions
7. Submit and review results

### For Deployment:
1. Update Azure App Service with new dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Add MongoDB Developer Associate Exam quiz type"
   git push
   ```
3. Deploy to Azure:
   ```bash
   ./deploy.sh
   ```

## Technical Details

### LLM Integration
- Model: `gemini-2.5-flash-lite`
- Agent: `mongo_quiz_generator`
- Session management: Per-user sessions with user-{user_id}-mongo pattern
- Prompt engineering: Structured prompts with documentation context
- JSON validation: Strict validation of question format

### Web Scraping
- Library: BeautifulSoup4 + lxml
- Target: mongodb.com/docs
- Content extraction: Title, paragraphs, code blocks
- Error handling: Fallback to default topics if fetching fails

### State Management
- Streamlit session state for quiz persistence
- MongoDB for quiz and score storage
- User fingerprinting with FingerprintJS
- Attempt tracking per quiz_type

## Known Limitations
1. Documentation fetching requires internet connection
2. Rate limiting may occur with mongodb.com
3. MSQ questions must match exactly (no partial credit)
4. Maximum 2 pages per topic to avoid context overflow

## Future Enhancements
1. Add more quiz types (e.g., AWS Certification, Python Certification)
2. Implement partial credit for MSQ
3. Add difficulty-based scoring weights
4. Cache documentation fetches to reduce API calls
5. Add quiz analytics dashboard
6. Support for image-based questions
