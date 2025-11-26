"""
MongoDB Exam Guide Loader

Loads and parses the MongoDB Developer Associate Exam guide
to extract topics, subtopics, and exam requirements.
"""
from pathlib import Path
from typing import Dict, List, Optional


def load_exam_guide(guide_path: Path) -> Dict[str, any]:
    """
    Load MongoDB exam guide from text file.
    
    Args:
        guide_path: Path to exam guide file
        
    Returns:
        Dictionary containing exam structure and requirements
    """
    if not guide_path.exists():
        return {
            'topics': [],
            'requirements': {},
            'content': ''
        }
    
    try:
        content = guide_path.read_text(encoding='utf-8')
        
        # Parse exam guide content
        # This is a simplified parser - adjust based on actual file format
        topics = extract_topics_from_guide(content)
        requirements = extract_requirements(content)
        
        return {
            'topics': topics,
            'requirements': requirements,
            'content': content
        }
    except Exception as e:
        print(f"Error loading exam guide: {e}")
        return {
            'topics': [],
            'requirements': {},
            'content': ''
        }


def extract_topics_from_guide(content: str) -> List[str]:
    """
    Extract exam topics/sections from MongoDB Developer Associate Exam Guide.
    
    Returns the official exam sections as defined in the guide.
    """
    # Official MongoDB Developer Associate Exam sections with weights
    # Based on the exam guide structure
    official_topics = [
        "MongoDB Overview and Document Model",  # 8%
        "CRUD",  # 51%
        "Indexes",  # 17%
        "Data Modeling",  # 4%
        "Tools and Tooling",  # 2%
        "Drivers"  # 18%
    ]
    
    # Try to extract sections from the guide content
    topics = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        # Look for "Section X:" pattern
        if line_stripped.startswith('Section ') and ':' in line_stripped:
            # Extract section name
            parts = line_stripped.split(':', 1)
            if len(parts) == 2:
                section_text = parts[1].strip()
                # Remove percentage if present (e.g., "(51%)")
                import re
                section_name = re.sub(r'\s*\(\d+%\)\s*$', '', section_text)
                if section_name:
                    topics.append(section_name)
    
    # Return extracted topics or official defaults
    return topics if topics else official_topics


def extract_requirements(content: str) -> Dict[str, any]:
    """
    Extract exam requirements from guide content.
    
    Returns:
        Dictionary with exam requirements following the official exam guide:
        - 53 total questions
        - Section weightings as per exam guide
        - question_types: MCQ and MSQ distribution
    """
    return {
        'total_questions': 53,
        'time_limit_minutes': 75,
        'section_weights': {
            'MongoDB Overview and Document Model': 0.08,  # 8% = ~4 questions
            'CRUD': 0.51,  # 51% = ~27 questions
            'Indexes': 0.17,  # 17% = ~9 questions
            'Data Modeling': 0.04,  # 4% = ~2 questions
            'Tools and Tooling': 0.02,  # 2% = ~1 question
            'Drivers': 0.18  # 18% = ~10 questions
        },
        'question_types': {
            'mcq': 0.6,  # 60% single-choice (Multiple Choice)
            'msq': 0.4   # 40% multi-select (Multiple Response)
        },
        'difficulty_levels': ['easy', 'medium', 'hard'],
        'default_difficulty': 'medium',
        'questions_per_topic': 2,  # For practice mode
        'mcq_options': 4,  # 1 correct + 3 distractors
        'msq_correct_range': (2, 3),  # 2-3 correct answers as per exam guide
        'msq_distractor_range': (2, 4)  # 2-4 distractors
    }


def get_exam_info() -> str:
    """
    Get formatted exam information string.
    """
    return """
MongoDB Developer Associate Exam

Format:
- Multiple Choice Questions (MCQ): Select ONE correct answer
- Multiple Select Questions (MSQ): Select ALL that apply (2-3 correct answers)

Topics:
- CRUD Operations
- Aggregation Framework
- Indexes and Performance
- Data Modeling
- Transactions
- Replication and High Availability
- Sharding and Scalability
- MongoDB Drivers
- Security
- Performance Optimization

Each question is based on official MongoDB documentation.
"""
