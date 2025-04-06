# LMS AI Content Generator

A comprehensive solution for generating educational content using OpenAI's GPT-4o model. This project includes both a Python backend service for API access and a user-friendly GUI application for desktop use.

## Overview

This project offers two main components:

1. **Backend API Service**: A serverless function/service (Google Cloud Run) that provides endpoints for generating educational content
2. **Desktop GUI Application**: A modern user interface for easily generating and viewing content without coding knowledge

## Features

### Backend API
- Generate educational paragraphs on any topic
- Create well-formed multiple-choice questions with 4 options
- Generate comprehensive quizzes with multiple questions
- Support for additional context to guide content generation
- Structured JSON responses for easy integration

### GUI Application
- Modern, intuitive interface with a clean design
- Supports all content types provided by the API
- History tracking for previous content generation requests
- Raw JSON response viewer with syntax highlighting
- Copy-to-clipboard functionality
- Threading support for responsive UI during API calls

## Backend Technical Architecture

- **FastAPI**: Lightweight web framework for creating the API
- **OpenAI API**: Using GPT-4o to generate high-quality educational content
- **Structured Outputs**: Leveraging OpenAI's JSON Schema validation
- **Pydantic**: For request/response validation
- **Environment Variables**: For secure API key management
- **Cloud Run**: For scalable, serverless deployment

## Project Structure

```
project/
├── main.py                 # FastAPI application with endpoints
├── prompt_handler.py       # Helper functions for prompt management
├── prompt_templates.py     # System and user prompts for different content types
├── schemas.py              # Pydantic models for request/response validation
├── utils.py                # Utility functions for OpenAI API interaction
├── lms_content_gui.py      # GUI application for desktop use
├── requirements.txt        # Project dependencies
├── Dockerfile              # For Cloud Run deployment
└── README.md               # Project documentation
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- An OpenAI API key
- For GUI: tkinter (usually included with Python)

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

## Usage Options

### Option 1: Run Locally (API)

Start the server locally:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### Option 2: Run the GUI Application

Launch the desktop application:
```bash
python lms_content_gui.py
```

### Option 3: Deploy to Google Cloud Run

1. Build and deploy the Docker container:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lms-content-generator
   gcloud run deploy lms-content-generator \
     --image gcr.io/YOUR_PROJECT_ID/lms-content-generator \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Get your service URL from the command output

## GUI Application Usage

1. **Launch the application** using `python lms_content_gui.py`
2. **Enter your Cloud Run API URL** in the URL field (or use the local URL for testing)
3. **Create content** by:
   - Entering a topic
   - Selecting a content type (paragraph, question, or quiz)
   - Adding optional context
   - Clicking "Generate Content"
4. **Review the results** in the main display area
5. **View raw JSON** by clicking the "View Raw Response" button
6. **Access history** to recall and reuse previous requests

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

**Example Request**:
```bash
curl -X POST "YOUR_SERVICE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python Variables",
    "content_type": "paragraph",
    "context": "Explain for beginners"
  }'
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

## Creating a Standalone Executable for the GUI

You can create a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed lms_content_gui.py
```

The executable will be created in the `dist` folder.

## Limitations and Assumptions

- The service assumes the OpenAI API is available and responsive
- Content is generated in English by default
- The expected length of paragraphs is 100-200 words
- Multiple-choice questions have exactly 4 options
- Quizzes contain 5 questions by default (unless specified otherwise)
- GUI requires tkinter, which is usually included with Python installations

## Future Improvements

- Support for additional content types (e.g., true/false questions, fill-in-the-blanks)
- Multi-language support
- User feedback loop to improve content quality
- Caching frequently requested topics
- Additional customization options (difficulty level, target age group, etc.)
- Content filtering for educational appropriateness
- OAuth authentication for the API