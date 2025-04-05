import os
import logging
from typing import Union
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from dotenv import load_dotenv

from schemas import ContentRequest, ParagraphResponse, MultipleChoiceQuestion, QuizResponse
from prompt_templates import (
    PARAGRAPH_SYSTEM_PROMPT, MCQ_SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT,
    PARAGRAPH_USER_PROMPT, MCQ_USER_PROMPT, QUIZ_USER_PROMPT,
    get_context_text
)
from utils import generate_content, parse_json_response
from json_schemas import PARAGRAPH_SCHEMA, MCQ_SCHEMA, QUIZ_SCHEMA

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LMS AI Content Generator",
    description="API for generating educational content with AI",
    version="1.0.0",
)

# Validate that API key is set
def check_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not set in environment variables")
        raise HTTPException(status_code=500, detail="API key not configured")

@app.post(
    "/generate",
    response_model=Union[ParagraphResponse, MultipleChoiceQuestion, QuizResponse],
    summary="Generate educational content"
)
async def generate(request: ContentRequest, _: None = Depends(check_api_key)):
    """
    Generate educational content based on the specified topic and content type.
    
    - **topic**: Subject matter for the content
    - **content_type**: Type of content to generate (paragraph, multiple_choice_question, or quiz)
    - **context**: Optional additional instructions or context
    """
    try:
        # Validate content_type
        if request.content_type not in ["paragraph", "multiple_choice_question", "quiz"]:
            logger.error(f"Invalid content_type: {request.content_type}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid content_type. Must be one of: paragraph, multiple_choice_question, quiz"
            )
        
        # Format the context text if provided
        context_text = get_context_text(request.context)
        
        # Select appropriate prompts and schema based on content_type
        if request.content_type == "paragraph":
            system_prompt = PARAGRAPH_SYSTEM_PROMPT
            user_prompt = PARAGRAPH_USER_PROMPT.format(
                topic=request.topic,
                context_text=context_text
            )
            schema = PARAGRAPH_SCHEMA
            
        elif request.content_type == "multiple_choice_question":
            system_prompt = MCQ_SYSTEM_PROMPT
            user_prompt = MCQ_USER_PROMPT.format(
                topic=request.topic,
                context_text=context_text
            )
            schema = MCQ_SCHEMA
            
        elif request.content_type == "quiz":
            system_prompt = QUIZ_SYSTEM_PROMPT
            user_prompt = QUIZ_USER_PROMPT.format(
                topic=request.topic,
                context_text=context_text
            )
            schema = QUIZ_SCHEMA
            
        # Generate content with structured output schema
        content = await generate_content(system_prompt, user_prompt, schema)
        
        # Parse the JSON response
        response_json = parse_json_response(content)
        
        # For paragraphs, convert the structured output back to our API format
        if request.content_type == "paragraph":
            return ParagraphResponse(content=response_json["content"])
            
        # For MCQs, return the structured output (it already matches our API format)
        elif request.content_type == "multiple_choice_question":
            return MultipleChoiceQuestion(
                question_text=response_json["question_text"],
                options=response_json["options"],
                correct_answer_index=response_json["correct_answer_index"]
            )
            
        # For quizzes, return the structured output (it already matches our API format)
        elif request.content_type == "quiz":
            questions = []
            for q in response_json["questions"]:
                questions.append(MultipleChoiceQuestion(
                    question_text=q["question_text"],
                    options=q["options"],
                    correct_answer_index=q["correct_answer_index"]
                ))
                
            return QuizResponse(
                title=response_json["title"],
                questions=questions
            )
    
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}


# For local development
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# Entry point for Google Cloud Function deployment
def entry_point(request):
    return app(request)