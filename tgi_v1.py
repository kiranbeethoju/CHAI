import os
from datetime import datetime
from huggingface_hub import hf_hub_download
from text_generation import Client

print(f"Current working directory is {os.getcwd()}")

# Load environment variables from .env file available in same directory
print("Loading all env variables.....")

# Access .env variables
print("Accessing HF Token.....")

# Define model to be used
model_id = "bartowski/Meta-Llama-3.1-70B-Instruct-GGUF"
filename = "Meta-Llama-3.1-70B-Instruct-Q4_K_L.gguf"

# Download the model
print("Downloading model.....")
model_path = hf_hub_download(
    repo_id=model_id,
    filename=filename,
    cache_dir="models",
)

# Set up TGI server (you need to have TGI installed and running)
# This part depends on your specific setup and may require additional configuration
tgi_address = "http://localhost:8080"  # Adjust this to your TGI server address

# Create a client to interact with the TGI server
print("Setting up TGI client.....")
client = Client(tgi_address)

print(f"Process start time is {datetime.now()}")
st = datetime.now()

# Generate text
prompt = "Provide background on transformers."
print("Generating text.....")
output = client.generate(prompt, max_new_tokens=1024)

print(output.generated_text)

en = datetime.now()
print(f"Process end time is {datetime.now()}")
print(f"Total time is {en-st}")
