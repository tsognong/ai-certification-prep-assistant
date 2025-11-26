"""
MongoDB Question Generator

Generates MongoDB exam-style questions (MCQ and MSQ) based on
official documentation and exam requirements.
"""
from typing import Dict, List, Any
import json


def create_mongo_question_prompt(
    docs_context: str,
    topics: List[str],
    num_questions: int,
    difficulty: str,
    requirements: Dict,
    exam_guide_content: str = ""
) -> str:
    """
    Create prompt for generating MongoDB exam questions.
    
    Args:
        docs_context: Formatted MongoDB documentation
        topics: Selected exam topics
        num_questions: Number of questions to generate
        difficulty: Question difficulty level
        requirements: Exam requirements (question types, etc.)
        exam_guide_content: Official exam guide content with objectives
        
    Returns:
        Formatted prompt string
    """
    mcq_count = int(num_questions * requirements['question_types']['mcq'])
    msq_count = num_questions - mcq_count
    
    # Build topic distribution if section weights are provided (full exam mode)
    topic_distribution = ""
    if 'section_weights' in requirements and num_questions == 53:
        topic_distribution = "\n\nQUESTION DISTRIBUTION BY SECTION (Official Exam Weightings):\n"
        for topic, weight in requirements['section_weights'].items():
            question_count = int(num_questions * weight)
            topic_distribution += f"- {topic}: {question_count} questions ({int(weight*100)}%)\n"
    
    # Extract relevant exam objectives for selected topics
    exam_objectives = ""
    if exam_guide_content:
        exam_objectives = "\n\nOFFICIAL EXAM OBJECTIVES (MUST FOLLOW STRICTLY):\n"
        exam_objectives += "Each question MUST align with these official exam objectives:\n\n"
        exam_objectives += exam_guide_content
    
    prompt = f"""You are an expert MongoDB certification exam question writer.

CONTEXT - MongoDB Official Documentation:
{docs_context}{exam_objectives}

TASK:
Generate {num_questions} MongoDB Developer Associate exam questions.
Questions MUST be based on the OFFICIAL EXAM OBJECTIVES listed above.
Each question should directly test one or more specific objectives (e.g., 2.1, 2.3, 3.1, 6.5, etc.).

EXAM SECTIONS TO COVER:
{', '.join(topics)}{topic_distribution}

QUESTION DISTRIBUTION:
- {mcq_count} Multiple Choice Questions (MCQ) - single correct answer
- {msq_count} Multiple Select Questions (MSQ) - 2-3 correct answers

DIFFICULTY: {difficulty}

REQUIREMENTS:

1. QUESTION STYLE - PRACTICAL CODE-BASED WITH JAVA DRIVER (CRITICAL):
   - 70% of questions MUST include Java code snippets or MongoDB queries
   - Use MongoDB Java Driver syntax: MongoClient, MongoDatabase, MongoCollection<Document>, Filters, Updates, Aggregates
   - Include proper Java imports: com.mongodb.client.*, org.bson.Document, com.mongodb.client.model.*
   - Present realistic Java scenarios: "Given this Java code...", "What will this method return?", "Identify the correct syntax..."
   - Include collection schemas, document structures, and data examples
   - Test ability to read, interpret, and analyze Java driver code
   - Example formats:
     * "Given the following Java code using MongoDB driver: ... What does it do?"
     * "Which of these Document instantiations is correctly formatted in Java?"
     * "What will be the output after running this Java aggregation pipeline?"
     * "Identify the error in this Java MongoDB driver code"
     * "Complete this Java CRUD operation: ..."
   - Use markdown code blocks: ```java for Java code, ```javascript for shell
   - Include common Java patterns: try-catch blocks, connection pooling, POJO mapping

2. MCQ Format (type: "mcq"):
   - 1 correct answer
   - 3 plausible distractors based on common coding mistakes
   - All options must be code examples, query results, or technical answers
   - Distractors should reflect real programming errors or misconceptions

3. MSQ Format (type: "msq"):
   - Question must state "Select ALL that apply"
   - 2-3 correct answers
   - 2-4 distractors
   - Test multiple related concepts or code variations
   - Example: "Which of these update operations will succeed?"

4. General Rules:
   - Base questions STRICTLY on the provided exam objectives and documentation
   - Each question MUST map to specific exam objective(s) (e.g., "Tests objective 2.3: $set updates")
   - Every question should test PRACTICAL skills, not just theory
   - Include actual MongoDB commands, queries, and Java driver code
   - Use realistic collection names and field names
   - Test scenario-based problem solving aligned with exam objectives
   - Avoid pure memorization questions
   - Each question must cite the documentation URL(s) and exam objective(s) tested

OUTPUT FORMAT (with practical code examples):
Return a JSON array of question objects. Use \\n for newlines in questions and ``` for code blocks.

EXAMPLE - Practical MCQ with code:
[
  {{
    "type": "mcq",
    "question": "Given a collection `orders` with documents: `{{ orderId: 1, status: 'pending', amount: 250 }}`, what will this query return?\\n\\n```javascript\\ndb.orders.find({{ status: 'pending', amount: {{ $gt: 200 }} }})\\n```",
    "options": [
      "All pending orders with amount greater than 200",
      "All orders regardless of status with amount > 200",
      "Only orders with amount exactly 200 and pending status",
      "Orders with amount greater than or equal to 200"
    ],
    "correct_answers": ["All pending orders with amount greater than 200"],
    "explanation": "The query uses AND logic: status must be 'pending' AND amount must be greater than 200 using $gt operator. Tests objective 2.8 and 2.10: equality constraints and relational operators.",
    "exam_objectives": ["2.8", "2.10"],
    "sources": ["https://www.mongodb.com/docs/manual/reference/operator/query/gt/"]
  }},
  {{
    "type": "mcq",
    "question": "Which insertOne() syntax is correct for a `users` collection?",
    "options": [
      "db.users.insertOne({{ name: 'John', age: 30 }})",
      "db.users.insertOne([{{ name: 'John' }}])",
      "db.users.insertOne('name': 'John', 'age': 30)",
      "db.users.insertOne(name: 'John', age: 30)"
    ],
    "correct_answers": ["db.users.insertOne({{ name: 'John', age: 30 }})"],
    "explanation": "insertOne() requires a document object with curly braces, not an array or separate parameters.",
    "sources": ["https://www.mongodb.com/docs/manual/reference/method/db.collection.insertOne/"]
  }},
  {{
    "type": "msq",
    "question": "Select ALL that apply: In this aggregation, which stages are used correctly?\\n\\n```javascript\\ndb.sales.aggregate([\\n  {{ $match: {{ year: 2024 }} }},\\n  {{ $group: {{ _id: '$product', total: {{ $sum: '$quantity' }} }} }},\\n  {{ $sort: {{ total: -1 }} }}\\n])\\n```",
    "options": [
      "$match filters documents by year 2024",
      "$group sums quantities by product",
      "$sort orders by total descending",
      "$match removes the year field",
      "$sum calculates average"
    ],
    "correct_answers": ["$match filters documents by year 2024", "$group sums quantities by product", "$sort orders by total descending"],
    "explanation": "$match filters, $group with $sum aggregates, $sort with -1 is descending. $match doesn't remove fields, $sum doesn't calculate averages.",
    "sources": ["https://www.mongodb.com/docs/manual/aggregation/"]
  }}
]

CRITICAL:
- 70% questions MUST include code snippets with realistic scenarios
- Use \\n for line breaks, ``` for code blocks in JSON strings
- Return ONLY valid JSON
- correct_answers must ALWAYS be an array
- Include MongoDB shell syntax or driver code
- Base ALL content on the provided documentation

CODE SNIPPET VALIDATION RULES (CRITICAL):
- If you reference a code snippet in the question (e.g., "Consider this Java code snippet:", "Given this code:"), you MUST include the COMPLETE code block immediately after
- NEVER write phrases like "Consider this code snippet:" or "Given the following code:" without providing the actual code
- Code blocks MUST be complete and runnable (include all necessary imports, variable declarations, etc.)
- If the question mentions "the code above" or "this code", ensure the code is actually present
- Format: "Question text...\\n\\n```java\\n[ACTUAL CODE HERE]\\n```\\n\\nWhat does this do?"
- DO NOT use placeholder text like [code here], [...], or incomplete snippets
- If you cannot provide complete code, rephrase the question to not reference code
"""
    
    return prompt


def validate_mongo_questions(questions: List[Dict]) -> List[Dict]:
    """
    Validate and fix MongoDB question format.
    Convert answer text to indices if needed.
    Remove duplicate questions.
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        List of validated, deduplicated questions with indices as correct_answers
    """
    validated = []
    seen_questions = set()  # Track question text to avoid duplicates
    
    for q in questions:
        # Ensure required fields
        if not all(k in q for k in ['type', 'question', 'options', 'correct_answers']):
            continue
        
        # Ensure correct_answers is a list
        if not isinstance(q['correct_answers'], list):
            q['correct_answers'] = [q['correct_answers']]
        
        # Convert answer text to indices if they're strings
        options = q.get('options', [])
        correct_indices = []
        
        for ans in q['correct_answers']:
            if isinstance(ans, int):
                # Already an index
                correct_indices.append(ans)
            elif isinstance(ans, str):
                # It's answer text, find its index in options
                try:
                    # Try exact match first
                    idx = options.index(ans)
                    correct_indices.append(idx)
                except ValueError:
                    # Try case-insensitive or stripped match
                    ans_stripped = ans.strip().lower()
                    for i, opt in enumerate(options):
                        if opt.strip().lower() == ans_stripped:
                            correct_indices.append(i)
                            break
        
        # Update with indices
        q['correct_answers'] = correct_indices
        
        # Ensure sources is present
        if 'sources' not in q:
            q['sources'] = []
        elif not isinstance(q['sources'], list):
            q['sources'] = [q['sources']]
        
        # Validate question type
        if q['type'] not in ['mcq', 'msq']:
            q['type'] = 'mcq'  # Default to MCQ
        
        # Validate MCQ has exactly 1 correct answer
        if q['type'] == 'mcq' and len(q['correct_answers']) != 1:
            # Take first answer only
            q['correct_answers'] = [q['correct_answers'][0]]
        
        # Validate MSQ has 2-3 correct answers
        if q['type'] == 'msq':
            if len(q['correct_answers']) < 2:
                continue  # Skip invalid MSQ
            if len(q['correct_answers']) > 3:
                q['correct_answers'] = q['correct_answers'][:3]
        
        # Ensure explanation exists
        if 'explanation' not in q:
            q['explanation'] = "Refer to MongoDB documentation for details."
        
        # Check for duplicate questions
        question_text = q['question'].strip().lower()
        if question_text in seen_questions:
            continue  # Skip duplicate
        
        # Validate code snippet completeness
        # Check if question references code but doesn't include it
        code_reference_patterns = [
            'consider this', 'given this code', 'the following code', 
            'code snippet', 'this java code', 'the code above',
            'in this code', 'using this code'
        ]
        
        has_code_reference = any(pattern in question_text for pattern in code_reference_patterns)
        has_code_block = '```' in q['question']
        
        # If question mentions code but doesn't include it, skip
        if has_code_reference and not has_code_block:
            continue  # Skip questions with incomplete code references
        
        seen_questions.add(question_text)
        validated.append(q)
    
    return validated


def grade_mongo_quiz(
    questions: List[Dict],
    user_answers: List[Any]
) -> Dict[str, Any]:
    """
    Grade MongoDB quiz with support for MCQ and MSQ.
    
    Args:
        questions: List of question dictionaries
        user_answers: List of user answers (index matches question index)
        
    Returns:
        Dictionary with score, percentage, and detailed feedback in format compatible with UI
    """
    total_questions = len(questions)
    correct_count = 0
    details = []
    
    for i, q in enumerate(questions):
        user_answer = user_answers[i] if i < len(user_answers) else None
        correct_answers = q['correct_answers']
        question_type = q['type']
        
        is_correct = False
        
        if question_type == 'mcq':
            # MCQ: Single answer must match
            correct_index = correct_answers[0]
            
            # Ensure both are same type for comparison
            if user_answer is not None:
                try:
                    # Convert both to int for comparison
                    user_answer_int = int(user_answer)
                    correct_index_int = int(correct_index)
                    is_correct = user_answer_int == correct_index_int
                except (ValueError, TypeError):
                    # If conversion fails, compare as-is
                    is_correct = user_answer == correct_index
            else:
                is_correct = False
            
            details.append({
                'question': q['question'],
                'options': q.get('options', []),
                'type': 'mcq',
                'user_answer': user_answer,
                'correct_index': correct_index,
                'correct_answers': correct_answers,
                'is_correct': is_correct,
                'explanation': q.get('explanation', ''),
                'sources': q.get('sources', [])
            })
            
        elif question_type == 'msq':
            # MSQ: All correct answers must be selected, no incorrect ones
            if user_answer and isinstance(user_answer, list):
                try:
                    # Convert both to sets of integers for comparison
                    user_set = set(int(x) for x in user_answer)
                    correct_set = set(int(x) for x in correct_answers)
                    is_correct = user_set == correct_set
                except (ValueError, TypeError):
                    # If conversion fails, try direct comparison
                    user_set = set(user_answer)
                    correct_set = set(correct_answers)
                    is_correct = user_set == correct_set
            else:
                is_correct = False
            
            details.append({
                'question': q['question'],
                'options': q.get('options', []),
                'type': 'msq',
                'user_answers': user_answer if isinstance(user_answer, list) else [],
                'correct_answers': correct_answers,
                'is_correct': is_correct,
                'explanation': q.get('explanation', ''),
                'sources': q.get('sources', [])
            })
        
        if is_correct:
            correct_count += 1
    
    percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'total': total_questions,
        'correct': correct_count,
        'percent': percentage,
        'passed': percentage >= 70,  # MongoDB exam passing score
        'details': details
    }
