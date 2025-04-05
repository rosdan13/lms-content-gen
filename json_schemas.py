"""JSON Schema definitions for content generation."""

# Schema for paragraph response
PARAGRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["paragraph"]},
        "content": {"type": "string"}
    },
    "required": ["type", "content"],
    "additionalProperties": False
}

# Schema for multiple-choice question
MCQ_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["multiple_choice_question"]},
        "question_text": {"type": "string"},
        "options": {
            "type": "array",
            "items": {"type": "string"}
        },
        "correct_answer_index": {"type": "integer"}
    },
    "required": ["type", "question_text", "options", "correct_answer_index"],
    "additionalProperties": False
}

# Schema for quiz
QUIZ_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["quiz"]},
        "title": {"type": "string"},
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["multiple_choice_question"]},
                    "question_text": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "correct_answer_index": {"type": "integer"}
                },
                "required": ["type", "question_text", "options", "correct_answer_index"],
                "additionalProperties": False
            }
        }
    },
    "required": ["type", "title", "questions"],
    "additionalProperties": False
}