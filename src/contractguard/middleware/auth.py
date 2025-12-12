from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

from contractguard.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for operational endpoints
        if request.url.path in ["/healthz", "/readyz", "/version", "/metrics"]:
            return await call_next(request)
        
        # P0-001: No AUTH_MODE=none in production
        if settings.AUTH_MODE == "none":
            raise HTTPException(
                status_code=500,
                detail="AUTH_MODE=none not allowed"
            )
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        try:
            if settings.AUTH_MODE == "jwt":
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM],
                    issuer=settings.JWT_ISSUER
                )
                request.state.actor_id = payload.get("sub")
                request.state.scopes = payload.get("scope", "").split()
            elif settings.AUTH_MODE == "static":
                if token != "dev-token-12345":
                    raise HTTPException(status_code=401, detail="Invalid token")
                request.state.actor_id = "dev-user"
                request.state.scopes = ["compliance:read", "compliance:write"]
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return await call_next(request)
