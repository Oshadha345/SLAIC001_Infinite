"""
Kade Connect FastAPI Application
Main application entry point with all routers and middleware
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
# import sentry_sdk
# from sentry_sdk.integrations.fastapi import FastApiIntegration
# from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from backend.shared.config import settings
from backend.shared.database import init_db
from backend.services.auth.router import router as auth_router
from backend.services.products.router import router as products_router
from backend.services.inventory.router import router as inventory_router
from backend.services.users.router import router as users_router
from backend.services.orders.router import router as orders_router
from backend.agents.data_acquisition.router import router as data_acquisition_router
from backend.agents.budget_optimization.router import router as budget_optimization_router
from backend.agents.personalization.router import router as personalization_router
from backend.agents.logistics.router import router as logistics_router
from backend.agents.execution.router import router as execution_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Kade Connect API...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down Kade Connect API...")


# Initialize Sentry for error tracking (optional in development)
# Temporarily disabled due to compatibility issues with Python 3.13
# if settings.SENTRY_DSN and settings.ENVIRONMENT == "production":
#     sentry_sdk.init(
#         dsn=settings.SENTRY_DSN,
#         integrations=[
#             FastApiIntegration(auto_enabling_integrations=True),
#             SqlalchemyIntegration(),
#         ],
#         traces_sample_rate=0.1,
#         environment=settings.ENVIRONMENT,
#     )

# Create FastAPI application
app = FastAPI(
    title="Kade Connect API",
    description="AI-powered grocery shopping platform for Sri Lanka",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization",
        },
        {
            "name": "Products",
            "description": "Product catalog management",
        },
        {
            "name": "Inventory",
            "description": "Product inventory and pricing",
        },
        {
            "name": "Users",
            "description": "User profile management",
        },
        {
            "name": "Orders",
            "description": "Order management and tracking",
        },
        {
            "name": "AI Agents",
            "description": "AI-powered optimization and recommendations",
        },
    ],
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "service": "kade-connect-api",
        "version": "1.0.0"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Kade Connect API",
        "description": "AI-powered grocery shopping platform for Sri Lanka",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Include routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    products_router,
    prefix="/api/v1/products",
    tags=["Products"]
)

app.include_router(
    inventory_router,
    prefix="/api/v1/inventory",
    tags=["Inventory"]
)

app.include_router(
    orders_router,
    prefix="/api/v1/orders",
    tags=["Orders"]
)

# AI Agents endpoints
app.include_router(
    data_acquisition_router,
    prefix="/api/v1/agents/data-acquisition",
    tags=["AI Agents"]
)

app.include_router(
    budget_optimization_router,
    prefix="/api/v1/agents/budget-optimization",
    tags=["AI Agents"]
)

app.include_router(
    personalization_router,
    prefix="/api/v1/agents/personalization",
    tags=["AI Agents"]
)

app.include_router(
    logistics_router,
    prefix="/api/v1/agents/logistics",
    tags=["AI Agents"]
)

app.include_router(
    execution_router,
    prefix="/api/v1/agents/execution",
    tags=["AI Agents"]
)

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return HTTPException(
        status_code=404,
        detail="The requested resource was not found"
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail="Internal server error occurred"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
