docker run --gpus all --shm-size 1g -ti -p 8080:80 \
  -v hf_cache:/data \
  -e MODEL_ID=hugging-quants/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4 \
  -e NUM_SHARD=4 \
  -e QUANTIZE=gptq \
  -e HF_TOKEN=$(cat ~/.cache/huggingface/token) \
  -e MAX_INPUT_LENGTH=4000 \
  -e MAX_TOTAL_TOKENS=4096 \
  ghcr.io/huggingface/text-generation-inference:2.2.0
