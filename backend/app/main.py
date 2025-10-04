import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from .api.ingest import router as ingest_router
from .api.reviews import router as reviews_router
from .api.search import router as search_router
from .api.analytics import router as analytics_router
from .middleware import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

# Load environment variables
load_dotenv()

app = FastAPI(
    title='Reviews Copilot API',
    description='Multi-location business review management system with AI-powered features',
    version='1.0.0',
    docs_url=None,  # Disable default docs to create custom one
    openapi_url="/openapi.json"
)

# Override OpenAPI schema to use 3.0.2 for better Swagger UI compatibility
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.2"
    )
    # Ensure proper OpenAPI 3.0.2 format
    openapi_schema["openapi"] = "3.0.2"
    
    # Clean up any 3.1.0 specific fields that might cause issues
    if "webhooks" in openapi_schema:
        del openapi_schema["webhooks"]
    
    # Ensure components section is properly formatted for 3.0.2
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        for schema_name, schema in openapi_schema["components"]["schemas"].items():
            # Remove 3.1.0 specific fields
            if isinstance(schema, dict):
                schema.pop("$anchor", None)
                schema.pop("unevaluatedProperties", None)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add custom exception handler for validation errors to ensure consistent error format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error occurred"}
    )

# Configure CORS
# In production, CORS_ORIGINS should be set to specific domain(s)
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(reviews_router)
app.include_router(search_router)
app.include_router(analytics_router)

@app.get('/docs', response_class=HTMLResponse, include_in_schema=False)
def custom_swagger_ui_html(request: Request):
    """Custom Swagger UI that works correctly behind reverse proxy"""
    # Use relative path to work with both direct access and proxy
    openapi_url = "./openapi.json"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Reviews Copilot API - Swagger UI</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
        dom_id: '#swagger-ui',
        layout: 'BaseLayout',
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        syntaxHighlight: {{
            theme: 'arta'
        }},
        tryItOutEnabled: true
    }});
    </script>
    </body>
    </html>
    """

@app.get('/health')
def health():
    return {'status': 'ok'}

