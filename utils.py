import os
import json
import logging
from typing import Dict, Any
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_content(system_prompt: str, user_prompt: str, 
                           schema: Dict[str, Any] = None, schema_name: str = None) -> str:
    """
    Generate content using OpenAI's API with the given prompts and JSON schema
    
    Args:
        system_prompt: The system prompt defining the AI's role and instructions
        user_prompt: The user prompt containing the specific request
        schema: JSON schema to constrain the model's output (for Structured Outputs)
        
    Returns:
        The generated content as a string
        
    Raises:
        Exception: If there's an error with the OpenAI API call
    """
    try:
        logger.info(f"Generating content with OpenAI: {user_prompt[:50]}...")
        
        # Prepare API call parameters
        params = {
            "model": "gpt-4o",  # Using the specified model
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
           # "temperature": 0.7,  # Moderate creativity
           # "max_tokens": 1000,  # Adjust as needed
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
        
        # Make the API call
        response = client.responses.create(**params)
        # Check for refusals or incomplete responses
        if response.status == "incomplete":
            reason = response.incomplete_details.reason
            logger.error(f"Incomplete response: {reason}")
            raise Exception(f"Failed to generate complete content: {reason}")
        if(response.output[0].content[0].type == "refusal"):
            logger.error(f"Model refused to answer")
            raise Exception(f"Model refused to answer: {response.output[0].content[0].refusal}")
        
        # Get the content
        content = response.output_text
        logger.info(f"Content generated successfully: {len(content)} chars")
        
        return content
        
    except Exception as e:
        logger.error(f"Error generating content with OpenAI: {str(e)}")
        raise Exception(f"Failed to generate content: {str(e)}")


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
        return json.loads(response_text)
            
    except Exception as e:
        logger.error(f"Error parsing JSON response: {str(e)}")
        logger.error(f"Response text: {response_text}")
        raise ValueError(f"Failed to parse response as JSON: {str(e)}")