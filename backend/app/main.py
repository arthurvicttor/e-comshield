from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.predict import router as predict_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter


app = FastAPI(
    title="E-ComShield API",
    description="Backend API for the E-ComShield system",
    version="0.1.0",
)

# Adiciona o limitador de taxa ao estado do aplicativo
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# Adiciona o middleware CORS para permitir solicitações do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Adiciona o middleware de segurança para definir cabeçalhos de segurança
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response: Response = await call_next(request)

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'"
    )

    return response


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(orders_router)