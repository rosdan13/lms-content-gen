# LMS AI Content Generator

A Python backend service for generating educational content using OpenAI's GPT-4o model. This service is designed to be deployed as a serverless function (Google Cloud Function or Cloud Run service) and provides an API endpoint for generating paragraphs, multiple-choice questions, and quizzes based on specified topics.

## Features

- Generate educational paragraphs on any topic
- Create well-formed multiple-choice questions with 4 options
- Generate comprehensive quizzes with multiple questions
- Support for additional context to guide content generation
- Structured JSON responses for easy integration with frontend components

## Technical Architecture

- **FastAPI**: Lightweight web framework for creating the API
- **OpenAI API**: Using GPT-4o to generate high-quality educational content
- **Pydantic**: For request/response validation
- **Environment Variables**: For secure API key management
- **Comprehensive Logging**: For debugging and monitoring
- **Error Handling**: Graceful handling of edge cases

## Project Structure

```
project/
├── main.py            # FastAPI application with endpoints
├── schemas.py         # Pydantic models for request/response validation
├── prompt_templates.py # System and user prompts for different content types
├── utils.py           # Utility functions for OpenAI API interaction
├── requirements.txt   # Project dependencies
├── .env               # Environment variables (not committed to version control)
└── README.md          # Project documentation
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- An OpenAI API key

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/lms-ai-content-generator.git
   cd lms-ai-content-generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running Locally

Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## API Usage

### Generate Endpoint

**Endpoint**: `POST /generate`

**Request Body**:
```json
{
  "topic": "string",
  "content_type": "string",
  "context": "string (optional)"
}
```

Where:
- `topic`: The subject matter for the content
- `content_type`: One of: `paragraph`, `multiple_choice_question`, or `quiz`
- `context` (optional): Additional instructions or context

**Example Requests**:

1. Generate a paragraph:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python Variables",
    "content_type": "paragraph",
    "context": "Explain for beginners"
  }'
```

2. Generate a multiple-choice question:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Photosynthesis",
    "content_type": "multiple_choice_question",
    "context": "High school level"
  }'
```

3. Generate a quiz:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "World War II",
    "content_type": "quiz",
    "context": "Focus on key events and figures"
  }'
```

**Using Python Requests**:
```python
import requests
import json

url = "http://localhost:8000/generate"
payload = {
    "topic": "Introduction to Python Variables",
    "content_type": "paragraph",
    "context": "Explain for beginners"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=2))
```

## Response Examples

### Paragraph Response
```json
{
  "type": "paragraph",
  "content": "Python variables are containers that store data values. Unlike in some programming languages, Python variables don't need explicit declaration to reserve memory space. You simply assign a value to a variable, and Python automatically creates it with the appropriate data type. For example, writing x = 5 creates a variable named 'x' that holds the integer value 5. Variables can store different types of data such as numbers, text (strings), lists, or more complex objects. They act as labels pointing to data in memory, allowing programmers to use meaningful names instead of memory addresses. This makes code more readable and maintainable, especially for beginners who are just starting to learn programming concepts."
}
```

### Multiple Choice Question Response
```json
{
  "type": "multiple_choice_question",
  "question_text": "Which process in photosynthesis captures light energy and converts it to chemical energy?",
  "options": [
    "Calvin cycle",
    "Light-dependent reactions",
    "Cellular respiration",
    "Transpiration"
  ],
  "correct_answer_index": 1
}
```

### Quiz Response
```json
{
  "type": "quiz",
  "title": "World War II: Key Events and Figures",
  "questions": [
    {
      "type": "multiple_choice_question",
      "question_text": "When did World War II begin in Europe?",
      "options": [
        "September 1, 1939",
        "December 7, 1941",
        "June 6, 1944",
        "August 6, 1945"
      ],
      "correct_answer_index": 0
    },
    {
      "type": "multiple_choice_question",
      "question_text": "Who was the Prime Minister of the United Kingdom for most of World War II?",
      "options": [
        "Neville Chamberlain",
        "Winston Churchill",
        "Clement Attlee",
        "Franklin D. Roosevelt"
      ],
      "correct_answer_index": 1
    },
    // ... more questions
  ]
}
```

## Prompt Engineering Approach

### Paragraph Generation
For paragraph generation, the prompt instructs the model to:
- Create accurate, factual content
- Make it clear and well-structured
- Adjust to the educational level specified in the context
- Keep length reasonable (100-200 words)
- Return only the paragraph text with no additional commentary

### Multiple-Choice Question Generation
The MCQ prompt emphasizes:
- Creating unambiguous questions that test understanding
- Having exactly 4 options with only one correct answer
- Including plausible distractors (incorrect options)
- Structuring the response as valid JSON with the required fields

### Quiz Generation
The quiz prompt builds on the MCQ approach but adds:
- Creating 5 questions that cover different aspects of the topic
- Maintaining consistency in difficulty
- Ensuring each question follows the same JSON structure
- Providing a relevant title for the quiz

## Deployment to Google Cloud

### Cloud Function Deployment

The code is already structured for Google Cloud Function deployment. The `entry_point` function in `main.py` serves as the entry point.

1. Deploy using gcloud CLI:
   ```bash
   gcloud functions deploy lms-content-generator \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated \
     --entry-point entry_point \
     --set-env-vars OPENAI_API_KEY=your_api_key_here
   ```

### Cloud Run Deployment

To deploy as a Cloud Run service:

1. Create a Dockerfile:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. Build and deploy:
   ```bash
   gcloud builds submit --tag gcr.io/your-project/lms-content-generator
   gcloud run deploy lms-content-generator \
     --image gcr.io/your-project/lms-content-generator \
     --platform managed \
     --set-env-vars OPENAI_API_KEY=your_api_key_here
   ```

## Limitations and Assumptions

- The service assumes the OpenAI API is available and responsive
- Content is generated in English by default
- The expected length of paragraphs is 100-200 words
- Multiple-choice questions have exactly 4 options
- Quizzes contain 5 questions
- JSON parsing may occasionally fail if the model doesn't adhere to the requested format
- The service does not verify the factual accuracy of generated content

## Future Improvements

- Support for additional content types (e.g., true/false questions, fill-in-the-blanks)
- Multi-language support
- User feedback loop to improve content quality
- Caching frequently requested topics
- Additional customization options (difficulty level, target age group, etc.)
- Content filtering for educational appropriateness
