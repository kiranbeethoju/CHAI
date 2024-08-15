import os
import sys
from datetime import datetime

# Install required packages if not already installed
required_packages = ['ctransformers', 'huggingface_hub']
for package in required_packages:
    if package not in sys.modules:
        print(f"Installing {package}...")
        os.system(f"pip install {package}")

from ctransformers import AutoModelForCausalLM
from huggingface_hub import hf_hub_download

print(f"Current working directory is {os.getcwd()}")

# Define model to be used
repo_id = "bartowski/Meta-Llama-3.1-70B-Instruct-GGUF"
model_file = "Meta-Llama-3.1-70B-Instruct-Q4_K_L.gguf"

# Download the model if it's not already present
if not os.path.exists(model_file):
    print("Downloading the model...")
    hf_hub_download(repo_id=repo_id, filename=model_file)

# Load the model
print("Loading the model...")
model = AutoModelForCausalLM.from_pretrained(
    model_file,
    model_type="llama",
    gpu_layers=50  # Adjust this based on your GPU memory
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
