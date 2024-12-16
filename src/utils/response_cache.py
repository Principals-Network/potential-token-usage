from typing import Dict, Any
import json
import os
from datetime import datetime, timedelta

class ResponseCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration = timedelta(hours=24)
        self._init_cache()

    def _init_cache(self):
        """Initialize cache directory and load existing cache"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk"""
        cache_file = os.path.join(self.cache_dir, "response_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Convert string timestamps back to datetime
                    for key, value in cached_data.items():
                        value['timestamp'] = datetime.fromisoformat(value['timestamp'])
                    self.cache = cached_data
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.cache = {}

    def _save_cache(self):
        """Save cache to disk"""
        cache_file = os.path.join(self.cache_dir, "response_cache.json")
        try:
            # Convert datetime to string for JSON serialization
            cache_to_save = {}
            for key, value in self.cache.items():
                cache_to_save[key] = {
                    **value,
                    'timestamp': value['timestamp'].isoformat()
                }
            with open(cache_file, 'w') as f:
                json.dump(cache_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def get(self, key: str) -> str | None:
        """Get cached response if valid"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.cache_duration:
                return entry['response']
        return None

    def set(self, key: str, response: str):
        """Cache a response"""
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now()
        }
        self._save_cache()

    def clear(self):
        """Clear the cache"""
        self.cache = {}
        self._save_cache() 