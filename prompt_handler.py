from typing import Any, Dict
from schemas import *
from prompt_templates import *

def get_prompt_fields(content_type: str) -> tuple[str, str, str, Dict[str, Any]]:
    """
    Retrieve the appropriate prompts and schema for a given content type.
    
    This function serves as a central configuration point for mapping content types
    to their corresponding system prompts, user prompt templates, and JSON schemas.
    The returned values can be used to configure API calls to OpenAI.
    
    Args:
        content_type: A string indicating the type of content to generate.
                     Must be one of: "paragraph", "multiple_choice_question", or "quiz".
    
    Returns:
        A tuple containing:
        - system_prompt: The system prompt for OpenAI
        - user_prompt_template: The user prompt template (needs to be formatted with topic and context)
        - schema_name: The name of the JSON schema to be used (cotent_type is good enough for this)
        - json_schema: The JSON schema derived from the corresponding Pydantic model
    
    Example:
        >>> system_prompt, user_prompt_template, type_name, schema = get_prompt_fields("paragraph")
        >>> user_prompt = user_prompt_template.format(topic="Python Basics", context_text="For beginners")
    """
    if content_type == "paragraph":
        return (PARAGRAPH_SYSTEM_PROMPT, PARAGRAPH_USER_PROMPT, 
                content_type, ParagraphResponse.model_json_schema())
    elif content_type == "multiple_choice_question":
        return (MCQ_SYSTEM_PROMPT, MCQ_USER_PROMPT, 
                content_type, MultipleChoiceQuestion.model_json_schema())
    elif content_type == "quiz":
        return (QUIZ_SYSTEM_PROMPT, QUIZ_USER_PROMPT,
                content_type, QuizResponse.model_json_schema())
    else:
        return ("invalid", None, None, None)
    
def get_permitted_types() -> list[str]:
    """
    Return a list of all permitted content types.
    
    This function provides a centralized list of all content types supported
    by the LMS AI Content Generator. It's useful for validation and
    for generating documentation or UI elements that need to display
    available options.
    
    Returns:
        A list of strings representing the supported content types.
    
    Example:
        >>> valid_types = get_permitted_types()
        >>> if user_input not in valid_types:
        >>>     raise ValueError(f"Content type must be one of: {', '.join(valid_types)}")
    """
    return ["paragraph, multiple_choice_question, quiz"]

def get_context_text(context):
    """Format the context if provided, otherwise return empty string"""
    if context:
        return f"Context: {context}"
    return ""