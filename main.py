import os
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn
from dotenv import load_dotenv
from collections import OrderedDict

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

# Initialize cache with OrderedDict (FIFO behavior)
response_cache = OrderedDict()
CACHE_SIZE_LIMIT = 100

# Initialize conversation state tracker
last_saved_request = None
last_saved_response = None

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


def should_use_cache(context: str) -> bool:
    """Check if the request should use cache based on context field"""
    return context and context.strip().startswith("[cache=true]")


def should_use_state(context: str) -> bool:
    """Check if the request should use conversation state based on context field"""
    return context and context.strip().endswith("[state=true]")


def cache_key(content_request: ContentRequest) -> str:
    """Generate a unique key for caching based on request parameters"""
    return f"{content_request.topic}|{content_request.content_type}|{content_request.context}"


def add_to_cache(key: str, response: dict):
    """Add a response to the cache with FIFO behavior"""
    global response_cache
    
    # If cache is at capacity, remove oldest item (first added)
    if len(response_cache) >= CACHE_SIZE_LIMIT:
        response_cache.popitem(last=False)
    
    # Add new item to cache
    response_cache[key] = response
    logger.info(f"Added response to cache. Cache size: {len(response_cache)}")


def apply_conversation_state(content_request: ContentRequest):
    """Apply conversation state to the request if needed"""
    global last_saved_request, last_saved_response
    
    # Only apply state if conditions are met
    if (last_saved_request and last_saved_response and 
        content_request.topic == last_saved_request.topic):
        
        # Create a summary of the previous interaction
        prev_context = last_saved_request.context or ""
        # Remove the state marker for better readability
        prev_context = prev_context.replace("[state=true]", "").strip()
        
        # Format last request and response as context
        state_context = f"""
Previous request:
Topic: {last_saved_request.topic}
Content type: {last_saved_request.content_type}
Context: {prev_context}

Previous response:
{last_saved_response}

Current request:
"""
        # Modify the context to include previous state
        # Remove the state marker first, then add it back later
        current_context = content_request.context.replace("[state=true]", "").strip()
        content_request.context = f"{state_context}{current_context}[state=true]"
        
        logger.info("Applied conversation state to request")


def prepare_generation_params(content_request, request_id):
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


def process_response(content, request_id):
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
    global last_saved_request, last_saved_response
    
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
        # Caching and Conversation State are naturally mutually exclusive,
        # because in a conversation 2 identical requests could have completely
        # different meanings depending on previous context.
        # Therefore, when conversation state is enabled caching will not take place.
        state_enabled = should_use_state(content_request.context)
        cache_enabled = should_use_cache(content_request.context)
       
        # Apply conversation state if needed
        if state_enabled:
            cache_enabled = False
            apply_conversation_state(content_request)
        
        # Check if we should use the cache
        if cache_enabled:
            cache_key_value = cache_key(content_request)
            if cache_key_value in response_cache:
                logger.info("Cache hit - returning cached response", extra={
                    "request_id": request_id,
                    "cache_key": cache_key_value
                })
                
                return response_cache[cache_key_value]
        
        # Step 1: Prepare generation parameters
        params = prepare_generation_params(content_request, request_id)
        
        # Step 2: Generate content
        content = await generate_ai_content(params, request_id)
        
        # Step 3: Process and return the response
        response = process_response(content, request_id)
        
        # Add to cache if caching is enabled
        if cache_enabled:
            add_to_cache(cache_key(content_request), response)
        
        # Update last request and response for conversation state
        if state_enabled:
            last_saved_request = content_request
            last_saved_response = response
        
        return response
        
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