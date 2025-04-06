import os
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn
from dotenv import load_dotenv

# Import the custom cloud logger
from cloud_logger import logger
from prompt_handler import get_prompt_fields, get_permitted_types, get_context_text
from schemas import ContentRequest
from utils import generate_content, parse_json_response
from utils import OpenAIConnectionError, OpenAIResponseError, OpenAIRefusalError

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LMS AI Content Generator",
    description="API for generating educational content with AI",
    version="1.0.0",
)

# Custom exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for FastAPI's validation errors
    Logs the error and returns a clean error response
    """
    request_id = os.urandom(8).hex()
    error_details = str(exc)
    
    logger.error("Request validation error", extra={
        "request_id": request_id,
        "client_host": request.client.host if request.client else "unknown",
        "path": request.url.path,
        "error_details": error_details
    })
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Invalid request format",
            "detail": "The request does not match the expected schema. Please check your request body.",
            "errors": error_details
        }
    )

# Validate that API key is set
def check_api_key():
    """Validate that the OpenAI API key is set in environment variables"""
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not set in environment variables", 
                   extra={"environment": os.environ.get("K_SERVICE", "local")})
        raise HTTPException(status_code=500, detail="API key not configured")


async def prepare_generation_params(content_request, request_id):
    """Prepare parameters for content generation"""
    # Get the right prompt fields for the type of content
    system_prompt, user_prompt, schema_name, schema = get_prompt_fields(content_request.content_type)
    
    # Validate content_type
    if system_prompt == "invalid":
        logger.error("Invalid content_type", extra={
            "request_id": request_id,
            "content_type": content_request.content_type,
            "permitted_types": get_permitted_types()
        })
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid content_type. Must be one of: " + str(get_permitted_types())
        )
        
    # Format the context text if provided
    context_text = get_context_text(content_request.context)

    # Prepare the user prompt to include all relevant information
    user_prompt = user_prompt.format(topic=content_request.topic, context_text=context_text)
    
    logger.info("Content generation parameters prepared", extra={
        "request_id": request_id,
        "content_type": content_request.content_type,
        "topic_length": len(content_request.topic),
        "context_provided": bool(context_text)
    })
    
    return system_prompt, user_prompt, schema_name, schema


async def generate_ai_content(params, request_id):
    """Generate content using OpenAI with proper error handling"""
    system_prompt, user_prompt, schema_name, schema = params
    
    logger.info("Starting content generation", extra={
        "request_id": request_id,
        "has_schema": schema is not None
    })
    
    start_time = time.time()
    
    try:
        content = await generate_content(system_prompt, user_prompt, schema, schema_name)
        generation_time = time.time() - start_time
        
        logger.info("Content generation completed", extra={
            "request_id": request_id,
            "generation_time_seconds": round(generation_time, 2),
            "content_length": len(content)
        })
        
        return content
        
    except OpenAIConnectionError as e:
        logger.error("OpenAI connection error", extra={
            "request_id": request_id,
            "error": str(e),
            "generation_time_seconds": round(time.time() - start_time, 2)
        })
        raise HTTPException(status_code=503, detail=f"OpenAI service unavailable: {str(e)}")
        
    except OpenAIResponseError as e:
        logger.error("OpenAI response error", extra={
            "request_id": request_id,
            "error": str(e),
            "generation_time_seconds": round(time.time() - start_time, 2)
        })
        raise HTTPException(status_code=500, detail=f"Error from OpenAI service: {str(e)}")
        
    except OpenAIRefusalError as e:
        logger.error("Content generation refused", extra={
            "request_id": request_id,
            "error": str(e),
            "generation_time_seconds": round(time.time() - start_time, 2)
        })
        raise HTTPException(status_code=422, detail=f"Content generation refused: {str(e)}")


async def process_response(content, request_id):
    """Process and parse the generated content"""
    try:
        response_json = parse_json_response(content)
        
        logger.info("Response processing completed", extra={
            "request_id": request_id,
            "response_type": response_json.get("type", "unknown")
        })
        
        return response_json
    except ValueError as e:
        logger.error("JSON parsing error", extra={
            "request_id": request_id,
            "error": str(e)
        })
        raise HTTPException(status_code=422, detail=f"Failed to parse generated content: {str(e)}")


@app.post(
    "/generate",
    summary="Generate educational content"
)
async def generate(content_request: ContentRequest, _: None = Depends(check_api_key)):
    """
    Generate educational content based on the specified topic and content type.
    
    - **topic**: Subject matter for the content
    - **content_type**: Type of content to generate (paragraph, multiple_choice_question, or quiz)
    - **context**: Optional additional instructions or context
    """
    # Generate unique ID for request tracking
    request_id = os.urandom(8).hex()
    
    # Log the validated request
    logger.info("Content generation request received", extra={
        "request_id": request_id,
        "topic": content_request.topic,
        "content_type": content_request.content_type,
        "has_context": content_request.context is not None
    })
    
    try:
        # Step 1: Prepare generation parameters
        params = await prepare_generation_params(content_request, request_id)
        
        # Step 2: Generate content
        content = await generate_ai_content(params, request_id)
        
        # Step 3: Process and return the response
        return await process_response(content, request_id)
        
    except HTTPException:
        # Re-raise HTTP exceptions that we've already created
        raise
        
    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception("Unexpected error", extra={
            "request_id": request_id,
            "error": str(e),
            "error_type": type(e).__name__
        })
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy"}


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up", extra={
        "environment": os.environ.get("K_SERVICE", "local"),
        "version": app.version
    })

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")


# For local development and Cloud Run
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)