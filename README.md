MouManTai

Insatllation guide:

```bash
pip install -r requirements.txt
# Install vLLM from pip:
pip install vllm

# Load and run the model:
vllm serve "mistralai/Mistral-7B-Instruct-v0.2"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "mistralai/Mistral-7B-Instruct-v0.2",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'
```

