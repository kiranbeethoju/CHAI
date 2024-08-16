import os
from openai import OpenAI

client = OpenAI(base_url="http://0.0.0.0:8000/v1", api_key=os.getenv("VLLM_API_KEY", "-"))

chat_completion = client.chat.completions.create(
  model="hugging-quants/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Deep Learning?"},
  ],
  max_tokens=128,
)
