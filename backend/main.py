import uvicorn
from backend.routes.account_routes import router as account_router
from backend.routes.tweet_routes import router as tweet_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os


load_dotenv()

db_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

app = FastAPI()
origins = [
    "https://twitterfromtemu-pi.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(account_router)
app.include_router(tweet_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)