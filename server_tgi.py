
#docker pull ghcr.io/huggingface/text-generation-inference:latest

import os
import subprocess
from datetime import datetime
from huggingface_hub import hf_hub_download
from text_generation import Client
import time

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

# Get the absolute path of the downloaded model
abs_model_path = os.path.abspath(model_path)

# Launch TGI server using Docker
print("Launching TGI server.....")
docker_command = f"""
docker run --gpus all --shm-size 1g -p 8080:80 \
    -v {abs_model_path}:/model \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id /model \
    --quantize bitsandbytes-nf4 \
    --max-input-length 4096 \
    --max-total-tokens 8192
"""

# Run the Docker command
process = subprocess.Popen(docker_command, shell=True)

# Wait for the server to start (adjust the sleep time if needed)
print("Waiting for TGI server to start.....")
time.sleep(30)

# Set up TGI client
tgi_address = "http://localhost:8080"
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

# Stop the Docker container
print("Stopping TGI server.....")
subprocess.run("docker stop $(docker ps -q --filter ancestor=ghcr.io/huggingface/text-generation-inference:latest)", shell=True)
