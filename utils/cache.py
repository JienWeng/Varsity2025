import json
from pathlib import Path
from typing import Dict, Any

class ResponseCache:
    def __init__(self, cache_file: str = "response_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, str] = self._load_cache()

    def _load_cache(self) -> Dict[str, str]:
        """Load cache from file if it exists."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Save cache to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get_cache_key(self, **kwargs) -> str:
        """Generate a unique cache key from the input parameters."""
        return json.dumps(kwargs, sort_keys=True)

    def get(self, key: str) -> str | None:
        """Get cached response if it exists."""
        return self.cache.get(key)

    def set(self, key: str, value: str):
        """Save response to cache."""
        self.cache[key] = value
        self._save_cache()