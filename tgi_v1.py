docker run --runtime nvidia --gpus all --ipc=host -p 8000:8000 \
  -v hf_cache:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model hugging-quants/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4 \
  --quantization gptq_marlin \
  --tensor-parallel-size 1 \
  --max-model-len 4096
