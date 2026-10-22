from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html
from fastapi.responses import Response

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.predict import router as predict_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.rate_limit import limiter

STATIC_DIR = Path(__file__).resolve().parent / "static" / "swagger"

app = FastAPI(
    title="E-ComShield API",
    description="Backend API for the E-ComShield system",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
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

    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='; "
    "style-src 'self' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "connect-src 'self' https://cdn.jsdelivr.net; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)

    return response

app.mount(
    "/static/swagger",
    StaticFiles(directory=str(STATIC_DIR)),
    name="swagger-static",
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        <title>E-ComShield API - Swagger UI</title>
        <link rel="stylesheet"
              href="/static/swagger/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="/static/swagger/swagger-ui-bundle.js"></script>
        <script src="/static/swagger/swagger-init.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_oauth_redirect():
    return get_swagger_ui_oauth2_redirect_html()

    
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)
app.include_router(orders_router)