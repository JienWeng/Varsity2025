from huggingface_hub import InferenceClient
from typing import List, Tuple
from utils.cache import ResponseCache

class ChatService:
    def __init__(self, model_name: str = "HuggingFaceH4/zephyr-7b-beta"):
        self.client = InferenceClient(model_name)
        self.cache = ResponseCache()

    def generate_response(
        self,
        message: str,
        history: List[Tuple[str, str]],
        system_message: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        # Create cache key from inputs
        cache_key = self.cache.get_cache_key(
            message=message,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )

        # Check cache first
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return cached_response

        # Prepare messages
        messages = [{"role": "system", "content": system_message}]
        for user_msg, assistant_msg in history:
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": message})

        # Generate response
        response = ""
        for message in self.client.chat_completion(
            messages,
            max_tokens=max_tokens,
            stream=True,
            temperature=temperature,
            top_p=top_p,
        ):
            token = message.choices[0].delta.content
            response += token

        # Cache the final response
        self.cache.set(cache_key, response)
        return response