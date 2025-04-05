from typing import List, Optional
from pydantic import BaseModel, Field

# Request Models
class ContentRequest(BaseModel):
    topic: str = Field(..., description="The subject matter for content generation")
    content_type: str = Field(..., description="Type of content to generate (paragraph, multiple_choice_question, or quiz)")
    context: Optional[str] = Field(None, description="Additional context or specific instructions")

# Response Models
class ParagraphResponse(BaseModel):
    type: str = "paragraph"
    content: str

class MultipleChoiceQuestion(BaseModel):
    type: str = "multiple_choice_question"
    question_text: str
    options: List[str]
    correct_answer_index: int

class QuizResponse(BaseModel):
    type: str = "quiz"
    title: str
    questions: List[MultipleChoiceQuestion]