from fastapi import FastAPI, Request
from pydantic import BaseModel
import time

app = FastAPI()

class Cache:
    def __init__(self, expiration_time: int = 60):
        self.cache = {}
        self.expiration_time = expiration_time

    def _invalidate(self):
        current_time = time.time()
        keys_to_delete = [key for key, value in self.cache.items() if current_time - value['timestamp'] > self.expiration_time]
        for key in keys_to_delete:
            del self.cache[key]

    def get(self, key: str):
        self._invalidate()
        if key in self.cache:
            return self.cache[key]['value']
        return None

    def set(self, key: str, value):
        self._invalidate()
        self.cache[key] = {'value': value, 'timestamp': time.time()}

cache = Cache()

class CacheItem(BaseModel):
    key: str
    value: str

@app.get("/cache/{key}")
def get_cache(key: str):
    value = cache.get(key)
    if value is not None:
        return {"key": key, "value": value}
    return {"error": "Key not found"}, 404

@app.post("/cache")
def set_cache(item: CacheItem):
    cache.set(item.key, item.value)
    return {"message": "Value set"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)