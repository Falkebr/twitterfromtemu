from fastapi import Request
from fastapi.routing import APIRoute

class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def log_request(request: Request):
            method = request.method
            path = request.url.path
            app.state.logs.append(f"{method} {path}")
            return await original_route_handler(request)

        return log_request