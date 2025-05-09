import time
from typing import Any, Dict

class Cache:
    def __init__(self, expiration_time: int = 60):
        """
        Initialize the cache with an expiration time in seconds.
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.expiration_time = expiration_time

    def _invalidate(self):
        """
        Invalidate cache entries older than the expiration time.
        """
        current_time = time.time()
        keys_to_delete = [key for key, value in self.cache.items() if current_time - value['timestamp'] > self.expiration_time]
        for key in keys_to_delete:
            del self.cache[key]

    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache if it exists and is not expired.
        """
        self._invalidate()
        if key in self.cache:
            return self.cache[key]['value']
        return None

    def set(self, key: str, value: Any):
        """
        Add a value to the cache with the current timestamp.
        """
        self._invalidate()
        self.cache[key] = {'value': value, 'timestamp': time.time()}

# Example usage
if __name__ == "__main__":
    cache = Cache()
    cache.set("key1", "value1")
    print(cache.get("key1"))  # Outputs: value1
    time.sleep(61)
    print(cache.get("key1"))  # Outputs: None (expired)