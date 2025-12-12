from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import time
import uuid

from contractguard.config import settings
from contractguard.middleware.auth import AuthMiddleware
from contractguard.middleware.tenant import TenantMiddleware
from contractguard.api import compliance, contracts, queries

app = FastAPI(
    title="ContractGuard API",
    version="0.1.0",
    description="Contract compliance checker"
)

# Middleware stack (order matters: last added = first executed)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuthMiddleware)

# Request ID + trace context
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = time.time()
    
    response = await call_next(request)
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = request_id
    
    duration = time.time() - request.state.start_time
    response.headers["X-Response-Time"] = f"{duration:.3f}"
    
    return response

# Routers
app.include_router(compliance.router, prefix="/v1/compliance", tags=["compliance"])
app.include_router(contracts.router, prefix="/v1/contracts", tags=["contracts"])
app.include_router(queries.router, prefix="/v1/queries", tags=["queries"])

# Operational endpoints
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    # TODO: Check DB, Redis, Vector DB connectivity
    return {"status": "ready"}

@app.get("/version")
async def version():
    return {
        "version": "0.1.0",
        "commit": settings.GIT_COMMIT,
        "build_time": settings.BUILD_TIME
    }

# Metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "internal_error",
            "message": "An unexpected error occurred",
            "details": {},
            "trace_id": getattr(request.state, "request_id", "unknown")
        }
    )
