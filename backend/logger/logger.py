from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
import uvicorn
from pydantic import BaseModel

class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def log_request(request: Request):
            method = request.method
            path = request.url.path
            # Use request.app.state.logs to ensure correct app instance
            request.app.state.logs.append(f"{method} {path}")
            return await original_route_handler(request)

        return log_request

class LogMessage(BaseModel):
    message: str

app = FastAPI()
app.state.logs = []
app.router.route_class = LoggingRoute

@app.get("/logs")
def get_logs():
    return app.state.logs

@app.post("/log")
def add_log(log: LogMessage):
    app.state.logs.append(log.message)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)