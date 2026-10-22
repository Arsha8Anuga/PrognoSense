import time
import json
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = round((time.time() - start_time) * 1000, 2)
        
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "endpoint": request.url.path,
            "status": response.status_code,
            "duration_ms": duration
        }
        
        try:
            with open("logs/requests.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
            
        return response