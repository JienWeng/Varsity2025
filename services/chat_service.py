import ollama
from codecarbon import EmissionsTracker
from typing import List, Tuple, Dict, Any
from utils.cache import ResponseCache

class ChatService:
    def __init__(self, model_name: str = "zephyr:latest"):
        self.model_name = model_name
        self.cache = ResponseCache()
        self.emissions_stats = {
            "total_emissions": 0.0,
            "total_energy": 0.0,
            "calls": 0,
            "cached_calls": 0,
            "emissions_saved": 0.0,
            "energy_saved": 0.0
        }

    def generate_response(
        self,
        message: str,
        history: List[Tuple[str, str]],
        system_message: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> Dict[str, Any]:
        cache_key = self.cache.get_cache_key(
            message=message,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )

        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.emissions_stats["cached_calls"] += 1
            carbon_data = self.cache.get_carbon_data(cache_key)
            return {
                "response": cached_response,
                "from_cache": True,
                "emissions": 0.0,
                "energy": 0.0,
                "emissions_saved": carbon_data.get("emissions", 0.0),
                "energy_saved": carbon_data.get("energy", 0.0)
            }

        # Prepare conversation history
        messages = [{"role": "system", "content": system_message}]
        for user_msg, assistant_msg in history:
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": message})

        # Start emissions tracking
        tracker = EmissionsTracker(save_to_file=True, output_dir="./emissions", log_level="warning")
        tracker.start()

        try:
            # Call Ollama
            response_data = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                }
            )

            response = response_data['message']['content']

            # Stop emissions tracker
            emissions_data = tracker.stop()

            # Extract emissions safely
            try:
                emissions = emissions_data.emissions if hasattr(emissions_data, 'emissions') else 0.0
                energy = emissions_data.energy_consumed if hasattr(emissions_data, 'energy_consumed') else 0.0
            except AttributeError:
                emissions = 0.0
                energy = 0.0

            self.emissions_stats["total_emissions"] += emissions
            self.emissions_stats["total_energy"] += energy
            self.emissions_stats["calls"] += 1

            self.cache.set(cache_key, response, emissions=emissions, energy=energy)

            return {
                "response": response,
                "from_cache": False,
                "emissions": emissions,
                "energy": energy,
                "emissions_saved": 0.0,
                "energy_saved": 0.0
            }

        except Exception as e:
            try:
                tracker.stop()
            except:
                pass
            raise e
