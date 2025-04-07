# LMS AI Content Generator

A comprehensive backend service and desktop application for generating educational content using OpenAI's GPT-4o model. This project directly addresses the requirements of developing an AI-powered content generation service for Learning Management Systems.

## Project Overview

This solution provides a serverless backend service that allows LMS content creators to generate educational content with minimal input. It includes both:

1. **Backend API Service**: A FastAPI-based serverless service deployable to Google Cloud Run that accepts HTTP requests and returns structured JSON responses
2. **Desktop GUI Application**: A user-friendly interface for testing and using the content generation capabilities without coding knowledge

## Core Features

### Content Generation

The service generates three types of educational content as required by the assignment:

- **Paragraphs**: Informative text content on any topic (100-200 words)
- **Multiple-Choice Questions**: Well-formed questions with 4 options and 1 correct answer
- **Quizzes**: Collections of multiple-choice questions with a title

### Request Processing

- Accepts HTTP POST requests with JSON payload containing:
  - `topic`: Subject matter for the content
  - `content_type`: Type of content to generate (`paragraph`, `multiple_choice_question`, or `quiz`)
  - `context` (Optional): Additional instructions or specific details

### Structured JSON Responses

Returns properly structured JSON responses according to specified schemas:

- **Paragraph Response**:
  ```json
  {
    "type": "paragraph",
    "content": "Generated text content for the paragraph..."
  }
  ```

- **Multiple Choice Question Response**:
  ```json
  {
    "type": "multiple_choice_question",
    "question_text": "The generated question?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer_index": 2
  }
  ```

- **Quiz Response**:
  ```json
  {
    "type": "quiz",
    "title": "Quiz Title related to the topic",
    "questions": [
      {
        "type": "multiple_choice_question",
        "question_text": "Question 1?",
        "options": ["A", "B", "C", "D"],
        "correct_answer_index": 0
      },
      // More questions...
    ]
  }
  ```

### Advanced Features

- **Effective Prompt Engineering**: Well-designed system and user prompts for high-quality content generation
- **API Key Management**: Secure handling of OpenAI API key using environment variables
- **Comprehensive Error Handling**: Robust error management for API failures, validation issues, and content refusals
- **Detailed Logging**: Structured logging with integration for Google Cloud Logging
- **Response Caching**: Optional caching mechanism to improve performance and reduce API costs
- **Conversation State Tracking**: Support for maintaining context across multiple requests

## Technical Architecture

### Backend Components

- **FastAPI**: Modern, high-performance web framework for building APIs
- **Pydantic**: Data validation and settings management
- **OpenAI API**: Integration with GPT-4o for content generation
- **Google Cloud Logging**: Structured logging for production environments
- **Docker**: Containerization for consistent deployment

### GUI Application

- **Tkinter**: Python's standard GUI toolkit
- **TTK Themed**: Modern styling for the interface
- **Threading**: Non-blocking UI during API calls
- **JSON Viewer**: Syntax highlighting for raw responses

## Project Structure

```
lms-content-generator/
├── main.py                 # FastAPI application with endpoints
├── prompt_handler.py       # Helper functions for prompt management
├── prompt_templates.py     # System and user prompts for content types
├── schemas.py              # Pydantic models for request/response validation
├── utils.py                # OpenAI API interaction utilities
├── cloud_logger.py         # Custom logging for Google Cloud
├── lms_content_gui.py      # GUI application for desktop use
├── requirements.txt        # Backend dependencies
├── requirements-full.txt   # Backend + GUI dependencies
├── Dockerfile              # For Cloud Run deployment
├── lms_config.txt          # Configuration file for GUI (required)
└── README.md               # Project documentation
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- An OpenAI API key
- For GUI: tkinter (usually included with Python)

### Installation

#### Linux

1. Clone the repository:
   ```bash
   git clone https://github.com/rosdan13/lms-content-gen.git
   cd lms-content-gen
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   - For backend only:
     ```bash
     pip install -r requirements.txt
     ```
   - For backend with GUI:
     ```bash
     pip install -r requirements-full.txt
     ```

4. Create a `.env` file with your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

#### Windows

1. Clone the repository:
   ```powershell
   git clone https://github.com/rosdan13/lms-content-gen.git
   cd lms-content-gen
   ```

2. Create a virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   - For backend only:
     ```powershell
     pip install -r requirements.txt
     ```
   - For backend with GUI:
     ```powershell
     pip install -r requirements-full.txt
     ```

4. Create a `.env` file with your OpenAI API key:
   ```powershell
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

## Running the Application Locally

### Backend API Service

#### Linux

1. Start the server:
   ```bash
   python main.py
   ```
   Or with uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Access the API documentation:
   - Open your browser and navigate to `http://localhost:8000/docs`

#### Windows

1. Start the server:
   ```powershell
   python main.py
   ```
   Or with uvicorn directly:
   ```powershell
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Access the API documentation:
   - Open your browser and navigate to `http://localhost:8000/docs`

### GUI Application

**Important Note**: To run the GUI application, you must have a file named `lms_config.txt` in the project directory. This file should contain the URL of the API service. The author will provide a pre-configured lms_config.txt file so that cloud functionality can be easily tested without requiring your own deployment.

#### Linux

1. Create the config file if it doesn't exist:
   ```bash
   echo "http://localhost:8000" > lms_config.txt
   ```

2. Launch the GUI:
   ```bash
   python lms_content_gui.py
   ```

#### Windows

1. Create the config file if it doesn't exist:
   ```powershell
   echo "http://localhost:8000" > lms_config.txt
   ```

2. Launch the GUI:
   ```powershell
   python lms_content_gui.py
   ```

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

### Health Check Endpoint

**Endpoint**: `GET /health`

Returns the API health status.

### Command Line Examples

#### Linux Terminal (curl)

1. **Generate a paragraph**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python Variables",
    "content_type": "paragraph",
    "context": "Explain for beginners"
  }'
```

2. **Generate a multiple-choice question**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Photosynthesis",
    "content_type": "multiple_choice_question",
    "context": "High school level"
  }'
```

3. **Generate a quiz**:
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "World War II",
    "content_type": "quiz",
    "context": "Focus on key events"
  }'
```

4. **Check API health**:
```bash
curl -X GET "http://localhost:8000/health"
```

#### Windows PowerShell

1. **Generate a paragraph**:
```powershell
$body = @{
    topic = "Introduction to Python Variables"
    content_type = "paragraph"
    context = "Explain for beginners"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/generate" -Method Post -Body $body -ContentType "application/json"
```

2. **Generate a multiple-choice question**:
```powershell
$body = @{
    topic = "Photosynthesis"
    content_type = "multiple_choice_question"
    context = "High school level"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/generate" -Method Post -Body $body -ContentType "application/json"
```

3. **Generate a quiz**:
```powershell
$body = @{
    topic = "World War II"
    content_type = "quiz"
    context = "Focus on key events"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/generate" -Method Post -Body $body -ContentType "application/json"
```

4. **Check API health**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

## Building and Deploying to Google Cloud Run

### Prerequisites

- Google Cloud SDK installed and configured
- Docker installed (for local building)
- A Google Cloud project with billing enabled
- Appropriate permissions to deploy to Cloud Run

### Deployment Steps

#### Linux

1. Build the Docker image locally (optional, can also use Cloud Build):
   ```bash
   docker build -t gcr.io/YOUR_PROJECT_ID/lms-content-generator .
   ```

2. Push the image to Google Container Registry:
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/lms-content-generator
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy lms-content-generator \
     --image gcr.io/YOUR_PROJECT_ID/lms-content-generator \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Alternatively, use Cloud Build to build and deploy in one step:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lms-content-generator
   gcloud run deploy lms-content-generator \
     --image gcr.io/YOUR_PROJECT_ID/lms-content-generator \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Get the service URL from the command output:
   ```bash
   gcloud run services describe lms-content-generator \
     --platform managed \
     --region us-central1 \
     --format="value(status.url)"
   ```

#### Windows

1. Build the Docker image locally (optional, can also use Cloud Build):
   ```powershell
   docker build -t gcr.io/YOUR_PROJECT_ID/lms-content-generator .
   ```

2. Push the image to Google Container Registry:
   ```powershell
   docker push gcr.io/YOUR_PROJECT_ID/lms-content-generator
   ```

3. Deploy to Cloud Run:
   ```powershell
   gcloud run deploy lms-content-generator `
     --image gcr.io/YOUR_PROJECT_ID/lms-content-generator `
     --platform managed `
     --region us-central1 `
     --allow-unauthenticated `
     --set-env-vars OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Alternatively, use Cloud Build to build and deploy in one step:
   ```powershell
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lms-content-generator
   gcloud run deploy lms-content-generator `
     --image gcr.io/YOUR_PROJECT_ID/lms-content-generator `
     --platform managed `
     --region us-central1 `
     --allow-unauthenticated `
     --set-env-vars OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Get the service URL from the command output:
   ```powershell
   gcloud run services describe lms-content-generator `
     --platform managed `
     --region us-central1 `
     --format="value(status.url)"
   ```

### Using the Deployed API

Once deployed, you can use the Cloud Run service URL to make requests to your API:

```bash
curl -X POST "https://lms-content-generator-xxxxxxxxxxxx.a.run.app/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python",
    "content_type": "paragraph"
  }'
```

## GUI Application Usage with Cloud Run

1. Update the `lms_config.txt` file with your Cloud Run URL:
   ```
   https://lms-content-generator-xxxxxxxxxxxx.a.run.app
   ```

2. Launch the GUI application:
   ```bash
   python lms_content_gui.py
   ```

3. The application will automatically load the API URL from the config file.

## Creating a Standalone Executable for the GUI

You can create a standalone executable using PyInstaller:

### Linux
```bash
pip install pyinstaller
pyinstaller --onefile --windowed lms_content_gui.py
```

### Windows
```powershell
pip install pyinstaller
pyinstaller --onefile --windowed lms_content_gui.py
```

The executable will be created in the `dist` folder.

## Advanced Features

### Response Caching

The service includes a caching mechanism to improve performance and reduce API costs:

- Add `[cache=true]` to the beginning of the context to enable caching
- Cached responses are stored in memory (up to 100 most recent requests)
- Identical requests (same topic, content type, and context) will return the cached response

### Conversation State Tracking

For context-aware content generation:

- Add `[state=true]` to the end of the context to enable conversation state
- Previous request/response pairs on the same topic will be included in the context
- Useful for building on previous content or creating related content

### GUI Features

- **Modern Interface**: Clean, intuitive design
- **Request History**: Track and reuse previous requests
- **Raw Response Viewer**: Examine the complete API response with syntax highlighting
- **Copy to Clipboard**: Easily export generated content
- **Threading Support**: UI remains responsive during API calls
- **Error Handling**: Clear error messages for troubleshooting

## Logging and Monitoring

The service includes comprehensive logging:

- Structured logs with request IDs
- Integration with Google Cloud Logging when deployed
- Console output for local development
- Error tracking and reporting
- Performance metrics (generation time, request processing)

## Limitations and Assumptions

- The service assumes the OpenAI API is available and responsive
- Content is generated in English by default
- The expected length of paragraphs is 100-200 words
- Multiple-choice questions have exactly 4 options
- Quizzes contain a default of 5 questions
- Cache and conversation state features cannot be used simultaneously
- API key should be properly secured in production environments
- For GUI application, `lms_config.txt` must exist in the project directory

## Security Considerations

- The service uses environment variables for API key management
- When deployed to Cloud Run, use Secret Manager for API key storage
- For production deployment, consider adding authentication to the API endpoints
