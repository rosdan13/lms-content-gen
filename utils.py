import os
import json
from typing import Dict, Any, Tuple
import openai
from openai import AuthenticationError, RateLimitError, BadRequestError, APIError

# Import the custom cloud logger
from cloud_logger import logger

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Custom exception classes for better error handling
class ContentGenerationError(Exception):
    """Base exception for content generation errors"""
    pass

class OpenAIConnectionError(ContentGenerationError):
    """Raised when there's a connection error to OpenAI"""
    pass

class OpenAIResponseError(ContentGenerationError):
    """Raised when OpenAI responds with an error"""
    pass

class OpenAIRefusalError(ContentGenerationError):
    """Raised when the model refuses to generate content"""
    pass


def prepare_openai_params(system_prompt: str, user_prompt: str, 
                         schema: Dict[str, Any] = None, 
                         schema_name: str = None) -> Dict[str, Any]:
    """
    Prepare parameters for OpenAI API call
    
    Args:
        system_prompt: The system prompt defining the AI's role
        user_prompt: The user prompt with the specific request
        schema: JSON schema for structured output
        schema_name: Name of the schema for structured output
        
    Returns:
        Dictionary with prepared API parameters
    """
    # Base parameters
    params = {
        "model": "gpt-4o",
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    }
    
    # Add structured output if schema is provided
    if schema and schema_name:
        params["text"] = {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": schema,
                "strict": True
            }
        }
    
    logger.info("OpenAI parameters prepared", extra={
        "prompt_length": len(user_prompt),
        "has_schema": schema is not None,
        "schema_name": schema_name
    })
    
    return params


async def call_openai_api(params: Dict[str, Any]) -> object:
    """
    Make the API call to OpenAI with proper error handling
    
    Args:
        params: Prepared parameters for the API call
        
    Returns:
        OpenAI API response object
        
    Raises:
        OpenAIConnectionError: For connection/authentication issues
        OpenAIResponseError: For API errors from OpenAI
    """
    try:
        response = client.responses.create(**params)
        logger.info("OpenAI API call successful")
        return response
        
    except AuthenticationError as e:
        logger.error("OpenAI authentication error", extra={"error": str(e)})
        raise OpenAIConnectionError(f"Authentication error: {str(e)}")
        
    except RateLimitError as e:
        logger.error("OpenAI rate limit exceeded", extra={"error": str(e)})
        raise OpenAIConnectionError(f"Rate limit exceeded: {str(e)}")
        
    except BadRequestError as e:
        logger.error("OpenAI bad request", extra={"error": str(e)})
        raise OpenAIResponseError(f"Bad request: {str(e)}")
        
    except APIError as e:
        logger.error("OpenAI API error", extra={"error": str(e)})
        raise OpenAIResponseError(f"API error: {str(e)}")
        
    except Exception as e:
        logger.error("OpenAI connection error", extra={
            "error": str(e), 
            "error_type": type(e).__name__
        })
        raise OpenAIConnectionError(f"Connection error: {str(e)}")


def process_openai_response(response: object) -> str:
    """
    Process the response from OpenAI, checking for errors or refusals
    
    Args:
        response: OpenAI API response object
        
    Returns:
        Generated content as a string
        
    Raises:
        OpenAIResponseError: For incomplete responses
        OpenAIRefusalError: When the model refuses to generate content
    """
    # Check for incomplete responses
    if response.status == "incomplete":
        reason = response.incomplete_details.reason
        logger.error("Incomplete response from OpenAI", extra={
            "reason": reason,
            "status": response.status
        })
        raise OpenAIResponseError(f"Failed to generate complete content: {reason}")
    
    # Check for content refusals
    if hasattr(response.output[0].content[0], 'type') and response.output[0].content[0].type == "refusal":
        refusal_message = response.output[0].content[0].refusal
        logger.error("Model refused to answer", extra={
            "refusal_message": refusal_message
        })
        raise OpenAIRefusalError(f"Model refused to answer: {refusal_message}")
    
    # Extract the content text
    content = response.output_text
    
    logger.info("Response processed successfully", extra={
        "content_length": len(content)
    })
    
    return content


async def generate_content(system_prompt: str, user_prompt: str, 
                          schema: Dict[str, Any] = None, 
                          schema_name: str = None) -> str:
    """
    Generate content using OpenAI's API with the given prompts and JSON schema
    
    Args:
        system_prompt: The system prompt defining the AI's role
        user_prompt: The user prompt with the specific request
        schema: JSON schema for structured output
        schema_name: Name of the schema for structured output
        
    Returns:
        The generated content as a string
        
    Raises:
        OpenAIConnectionError: For network/connection issues
        OpenAIResponseError: For API errors from OpenAI
        OpenAIRefusalError: When the model refuses to generate content
        ContentGenerationError: For other generation errors
    """
    try:
        # Step 1: Prepare the API parameters
        params = prepare_openai_params(system_prompt, user_prompt, schema, schema_name)
        
        # Step 2: Make the API call
        response = await call_openai_api(params)
        
        # Step 3: Process the response
        content = process_openai_response(response)
        
        logger.info("Content generated successfully", extra={
            "content_length": len(content),
            "output_type": "text" if not schema else schema_name
        })
        
        return content
        
    except (OpenAIConnectionError, OpenAIResponseError, OpenAIRefusalError):
        # Re-raise specific exceptions without wrapping
        raise
        
    except Exception as e:
        logger.exception("Unexpected error generating content", extra={
            "error_type": type(e).__name__,
            "error": str(e)
        })
        raise ContentGenerationError(f"Unexpected error generating content: {str(e)}")


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON from the response text
    
    Args:
        response_text: The text response from OpenAI
        
    Returns:
        The parsed JSON as a dictionary
        
    Raises:
        ValueError: If the response text can't be parsed as JSON
    """
    try:
        # With Structured Outputs, response should already be valid JSON
        parsed_json = json.loads(response_text)
        
        logger.info("Successfully parsed JSON response", extra={
            "json_keys": list(parsed_json.keys()),
            "response_type": parsed_json.get("type", "unknown")
        })
        
        return parsed_json
            
    except json.JSONDecodeError as e:
        log_json_parse_error(response_text, e)
        raise ValueError(f"Failed to parse response as JSON: {str(e)}")
        
    except Exception as e:
        log_json_parse_error(response_text, e)
        raise ValueError(f"Failed to parse response as JSON: {str(e)}")


def log_json_parse_error(response_text: str, error: Exception) -> None:
    """
    Log details about JSON parsing errors
    
    Args:
        response_text: The text that failed to parse
        error: The exception that was raised
    """
    logger.error("Error parsing JSON response", extra={
        "error_type": type(error).__name__,
        "error": str(error),
        "response_length": len(response_text),
        "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
    })
    
    # Log full response at debug level
    logger.debug("Full response text for debugging", extra={
        "response_text": response_text
    })