import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ctransformers import AutoModelForCausalLM
import uvicorn

# Define the model path
MODEL_PATH = "Meta-Llama-3.1-70B-Instruct-Q4_K_L.gguf"

# Check if the model file exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

# Load the model
print("Loading the model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="llama",
    gpu_layers=50  # Adjust based on your GPU memory
)

app = FastAPI()

class GenerationRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 1024

@app.post("/generate")
async def generate_text(request: GenerationRequest):
    try:
        response = model(request.prompt, max_new_tokens=request.max_new_tokens)
        return {"generated_text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
