import os
from openai import OpenAI

client = OpenAI(base_url="http://0.0.0.0:8080/v1", api_key=os.getenv("OPENAI_API_KEY", "-"))

chat_completion = client.chat.completions.create(
  model="tgi",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Deep Learning?"},
  ],
  max_tokens=128,
)
