import json
from pathlib import Path
from typing import Dict, Any, Optional

class ResponseCache:
    def __init__(self, cache_file: str = "response_cache.json", carbon_file: str = "carbon_cache.json"):
        self.cache_file = Path(cache_file)
        self.carbon_file = Path(carbon_file)
        self.cache: Dict[str, str] = self._load_cache()
        self.carbon_data: Dict[str, Dict[str, float]] = self._load_carbon_data()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load cache from file if it exists."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_carbon_data(self) -> Dict[str, Dict[str, float]]:
        """Load carbon data from file if it exists."""
        if self.carbon_file.exists():
            with open(self.carbon_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def _save_carbon_data(self):
        """Save carbon data to file."""
        with open(self.carbon_file, 'w') as f:
            json.dump(self.carbon_data, f)
    
    def get_cache_key(self, **kwargs) -> str:
        """Generate a unique cache key from the input parameters."""
        return json.dumps(kwargs, sort_keys=True)
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response if it exists."""
        return self.cache.get(key)
    
    def get_carbon_data(self, key: str) -> Dict[str, float]:
        """Get carbon data for a specific cache key."""
        return self.carbon_data.get(key, {"emissions": 0.0, "energy": 0.0})
    
    def get_total_carbon_data(self) -> Dict[str, float]:
        """Calculate total carbon emissions and energy consumption saved."""
        total_emissions = sum(data.get("emissions", 0.0) for data in self.carbon_data.values())
        total_energy = sum(data.get("energy", 0.0) for data in self.carbon_data.values())
        return {
            "total_emissions_saved": total_emissions,
            "total_energy_saved": total_energy,
            "cache_hits": len(self.cache)
        }
    
    def set(self, key: str, value: str, emissions: float = 0.0, energy: float = 0.0):
        """Save response to cache along with carbon emissions data."""
        self.cache[key] = value
        self.carbon_data[key] = {"emissions": emissions, "energy": energy}
        self._save_cache()
        self._save_carbon_data()