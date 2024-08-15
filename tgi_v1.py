import os
from datetime import datetime
from huggingface_hub import hf_hub_download
from text_generation import Client

print(f"Current working directory is {os.getcwd()}")
import os
import subprocess
import time
from datetime import datetime

from huggingface_hub import snapshot_download
from text_generation import Client

# Load environment variables
print("Loading environment variables...")

# Access Hugging Face token
hf_token = "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"
if not hf_token:
    raise ValueError("HUGGING_FACE_TOKEN not found in .env file")

# Model information
model_id = "hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4"

# Download the model
print(f"Downloading model {model_id}...")
model_path = snapshot_download(
    repo_id=model_id,
    token=hf_token,
    cache_dir="models",
    ignore_patterns=["*.md", "*.txt"]
)

# Get the absolute path of the downloaded model
abs_model_path = os.path.abspath(model_path)
print(f"Model downloaded to: {abs_model_path}")

# Launch TGI server using Docker
print("Launching TGI server...")
docker_command = f"""
docker run --gpus all --shm-size 1g -p 8080:80 \
    -v {abs_model_path}:/model \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id /model \
    --quantize awq \
    --max-input-length 4096 \
    --max-total-tokens 8192
"""

# Run the Docker command
process = subprocess.Popen(docker_command, shell=True)

# Wait for the server to start
print("Waiting for TGI server to start...")
time.sleep(60)  # Adjust this value if needed

# Set up TGI client
tgi_address = "http://localhost:8080"
print("Setting up TGI client...")
client = Client(tgi_address)

# Generate text
print("Generating text...")
prompt = "Explain the concept of quantum computing in simple terms."
st = datetime.now()
output = client.generate(prompt, max_new_tokens=1024)
en = datetime.now()

print("\nGenerated Text:")
print(output.generated_text)
print(f"\nGeneration time: {en - st}")

# Keep the script running to maintain the server
input("Press Enter to stop the server and exit...")

# Stop the Docker container
print("Stopping TGI server...")
subprocess.run("docker stop $(docker ps -q --filter ancestor=ghcr.io/huggingface/text-generation-inference:latest)", shell=True)

print("Server stopped. Exiting...")
