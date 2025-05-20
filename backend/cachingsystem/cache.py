from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
import requests

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

@app.get("/api/tweets")
def get_tweets():
    cached = cache.get("tweets")
    if cached is not None:
        print("[CACHE] HIT for /api/tweets")
        return cached
    print("[CACHE] MISS for /api/tweets, fetching from API...")
    try:
        resp = requests.get("http://api:8000/api/tweets", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            cache.set("tweets", data)
            print("[CACHE] Stored new data for /api/tweets")
            return data
        else:
            print(f"[CACHE] API returned status {resp.status_code}: {resp.text}")
            return {"error": f"API error: {resp.status_code}", "details": resp.text}, resp.status_code
    except Exception as e:
        print(f"[CACHE] Exception contacting API: {e}")
        return {"error": "Could not contact API", "details": str(e)}, 502

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_api(path: str, request: Request):
    # Special case: cache GET /api/tweets
    if request.method == "GET" and path == "tweets":
        cached = cache.get("tweets")
        if cached is not None:
            print("[CACHE] HIT for /api/tweets")
            return cached
        print("[CACHE] MISS for /api/tweets, fetching from API...")
        try:
            resp = requests.get(f"http://api:8000/api/tweets", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                cache.set("tweets", data)
                print("[CACHE] Stored new data for /api/tweets")
                return data
            else:
                print(f"[CACHE] API returned status {resp.status_code}: {resp.text}")
                return JSONResponse(content={"error": f"API error: {resp.status_code}", "details": resp.text}, status_code=resp.status_code)
        except Exception as e:
            print(f"[CACHE] Exception contacting API: {e}")
            return JSONResponse(content={"error": "Could not contact API", "details": str(e)}, status_code=502)
    # Proxy all other /api/* requests to the API service
    api_url = f"http://api:8000/api/{path}"
    try:
        method = request.method
        headers = dict(request.headers)
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        resp = requests.request(method, api_url, headers=headers, data=body, timeout=5)
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        print(f"[CACHE] Exception proxying {method} {api_url}: {e}")
        return JSONResponse(content={"error": "Proxy error", "details": str(e)}, status_code=502)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)