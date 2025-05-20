import uvicorn
from backend.routes.account_routes import router as account_router
from backend.routes.tweet_routes import router as tweet_router
from backend.likebatcher.likebatcher import start_batcher
from backend.logger.logger import LoggingRoute
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()
        async def log_request(request: Request):
            method = request.method
            path = request.url.path
            request.app.state.logs.append(f"{method} {path}")
            return await original_route_handler(request)
        return log_request

app = FastAPI()
app.state.logs = []
app.state.db_accesses = 0
app.router.route_class = LoggingRoute

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set LoggingRoute as the default route class
app.router.route_class = LoggingRoute

app.include_router(account_router)
app.include_router(tweet_router)

# Start like batching function
start_batcher()

app.state.logs = []

@app.get("/logs")
def get_logs():
    return {
        "api_calls": app.state.logs,
        "db_accesses": app.state.db_accesses
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)