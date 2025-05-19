import uvicorn
from backend.routes.account_routes import router as account_router
from backend.routes.tweet_routes import router as tweet_router
from backend.likebatcher.likebatcher import start_batcher
from backend.logger.logger import LoggingRoute
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
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
    return app.state.logs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)