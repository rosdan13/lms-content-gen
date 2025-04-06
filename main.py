import os
import logging
from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from dotenv import load_dotenv

from prompt_handler import get_prompt_fields, get_permitted_types, get_context_text
from schemas import ContentRequest
from utils import generate_content, parse_json_response

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
        # Get the right prompt fields for the type of content (paragraph, question, quiz)
        system_prompt, user_prompt, schema_name, schema = get_prompt_fields(request.content_type)
      
        # Validate content_type
        if system_prompt == "invalid":
            logger.error(f"Invalid content_type: {request.content_type}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid content_type. Must be one of:" + str(get_permitted_types())
            )
        
        # Format the context text if provided
        context_text = get_context_text(request.context)

        # prepare the user prompt to include all relevant information
        user_prompt = user_prompt.format(topic=request.topic, context_text = context_text)
 
        # Generate content with structured output schema
        content = await generate_content(system_prompt, user_prompt, schema, schema_name)
        
        # Parse the JSON response
        response_json = parse_json_response(content)
        
        # If no error was raised until this point, we can safely return the JSON response
        return response_json
    
    # Error Handling
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