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

async def generate_content(system_prompt: str, user_prompt: str) -> str:
    """
    Generate content using OpenAI's API with the given prompts
    
    Args:
        system_prompt: The system prompt defining the AI's role and instructions
        user_prompt: The user prompt containing the specific request
        
    Returns:
        The generated content as a string
        
    Raises:
        Exception: If there's an error with the OpenAI API call
    """
    try:
        logger.info(f"Generating content with OpenAI: {user_prompt[:50]}...")
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the specified model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Moderate creativity
            max_tokens=1000,  # Adjust as needed
        )
        
        content = response.choices[0].message.content
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
        # Try to find JSON if it's embedded in a larger text
        response_text = response_text.strip()
        
        # If response is wrapped in backticks or has extra text, try to extract just the JSON
        if "```json" in response_text and "```" in response_text.split("```json", 1)[1]:
            json_content = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
            return json.loads(json_content)
        elif "```" in response_text and "```" in response_text.split("```", 1)[1]:
            json_content = response_text.split("```", 1)[1].split("```", 1)[0].strip()
            return json.loads(json_content)
        else:
            # Try parsing the whole response as JSON
            return json.loads(response_text)
            
    except Exception as e:
        logger.error(f"Error parsing JSON response: {str(e)}")
        logger.error(f"Response text: {response_text}")
        raise ValueError(f"Failed to parse response as JSON: {str(e)}")
