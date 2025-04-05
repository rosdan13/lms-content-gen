import requests
import json

url = "http://localhost:8000/generate"

# Test paragraph generation
payload = {
    "topic": "Introduction to Python",
    "content_type": "paragraph",
    "context": "For beginners"
}
response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))

# Test multiple-choice question generation
payload = {
    "topic": "Photosynthesis",
    "content_type": "multiple_choice_question",
    "context": "High school level"
}
response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))