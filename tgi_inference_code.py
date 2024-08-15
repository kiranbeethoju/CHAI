import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
token = "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"
try:
    from datetime import datetime
    from ctransformers import AutoModelForCausalLM
except:
    os.system("pip install ctransformers")
print(f"Current working directory is {os.getcwd()}")

# Define model to be used
model_path = "Meta-Llama-3.1-70B-Instruct-Q4_K_L.gguf"

# Download the model if it's not already present
if not os.path.exists(model_path):
    print("Downloading the model...")
    # You may need to implement a download function here or use a library like `huggingface_hub`
    # For example: 
    from huggingface_hub import hf_hub_download
    hf_hub_download(repo_id="bartowski/Meta-Llama-3.1-70B-Instruct-GGUF", filename="Meta-Llama-3.1-70B-Instruct-Q4_K_L.gguf")

# Load the model
print("Loading the model...")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    model_type="llama",
    gpu_layers=50,
    token=token
)

# Function to generate text
def generate_text(prompt, max_new_tokens=1024):
    return model(prompt, max_new_tokens=max_new_tokens)

# Example usage
print(f"Process start time is {datetime.now()}")
st = datetime.now()

prompt = "Provide background on transformers."
response = generate_text(prompt)
print(response)

en = datetime.now()
print(f"Process end time is {datetime.now()}")
print(f"Total time is {en-st}")
