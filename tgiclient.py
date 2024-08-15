# Set up TGI client
import os
import subprocess
from datetime import datetime
from huggingface_hub import hf_hub_download
from text_generation import Client
import time
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
