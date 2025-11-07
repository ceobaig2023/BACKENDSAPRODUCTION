from fastapi import FastAPI
import requests
import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Load Hugging Face API details
HF_API_URL = os.getenv("LLM_API_URL", "https://api-inference.huggingface.co/models/facebook/bart-large-mnli")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

headers = {"Authorization": f"Bearer {HF_API_KEY}"}


class PromptInput(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {"message": "RAG / Hugging Face test API running 🚀"}


@app.post("/test-rag")
def test_rag(input: PromptInput):
    payload = {"inputs": input.prompt}

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            return {
                "status": "error",
                "details": response.text,
                "code": response.status_code
            }

        data = response.json()
        return {
            "status": "success",
            "prompt": input.prompt,
            "output": data
        }

    except Exception as e:
        return {"status": "error", "details": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("PromptInput:app", host="0.0.0.0", port=8005, reload=True)
