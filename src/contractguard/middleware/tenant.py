from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip for operational endpoints
        if request.url.path in ["/healthz", "/readyz", "/version", "/metrics"]:
            return await call_next(request)
        
        # Extract tenant from JWT claims or header
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if not tenant_id:
            # Fallback to X-Tenant-ID header
            tenant_id = request.headers.get("X-Tenant-ID")
        
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Missing tenant context")
        
        request.state.tenant_id = tenant_id
        
        return await call_next(request)
