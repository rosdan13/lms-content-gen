from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# Request Models
class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=10000, description="The subject matter for content generation")
    content_type: str = Field(..., description="Type of content to generate (paragraph, multiple_choice_question, or quiz)")
    context: Optional[str] = Field(None, max_length=10000, description="Additional context or specific instructions")
   
    model_config = {
    "extra": "forbid",
    "str_strip_whitespace": True,  # Automatically strip whitespace from all strings
    }
    
# Response Models
class ParagraphResponse(BaseModel):
    type: Literal["paragraph"]
    content: str

    class Config:
        extra = "forbid"  # This makes additionalProperties = False in JSON Schema

class MultipleChoiceQuestion(BaseModel):
    type: Literal["multiple_choice_question"]
    question_text: str
    options: List[str]
    correct_answer_index: int
    class Config:
        extra = "forbid"  # This makes additionalProperties = False in JSON Schema

class QuizResponse(BaseModel):
    type: Literal["quiz"]
    title: str
    questions: List[MultipleChoiceQuestion]
    class Config:
        extra = "forbid"  # This makes additionalProperties = False in JSON Schema