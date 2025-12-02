"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import get_client, close_connection
from .routers import businesses, reviews, users, discovery, semantic


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Test MongoDB connection on startup
    try:
        client = get_client()
        client.admin.command('ping')
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection warning: {e}")
    
    yield
    
    # Close connection on shutdown
    close_connection()
    print("MongoDB connection closed")


# Create FastAPI app
app = FastAPI(
    title="Yelp Dataset API",
    description="REST API for geo-distributed local discovery on Yelp dataset",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Core resource-style APIs
app.include_router(businesses.router)
app.include_router(reviews.router)
app.include_router(users.router)

# Compatibility / extended APIs from earlier design
# - /search/location
# - /business/{business_id}
# - /business/{business_id}/reviews
app.include_router(discovery.router)

# - /search/semantic
app.include_router(semantic.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Yelp Dataset API",
        "version": "1.0.0",
        "description": "REST API for geo-distributed local discovery",
        "endpoints": {
            "businesses": {
                "search_by_location": "/businesses/search/location?latitude={lat}&longitude={lon}&radius={km}",
                "search_by_region": "/businesses/search/region?state={state}&city={city}&category={cat}",
                "get_by_id": "/businesses/{business_id}",
                "create": "POST /businesses"
            },
            "reviews": {
                "get_by_business": "/reviews/business/{business_id}",
                "create": "POST /reviews"
            },
            "users": {
                "get_by_id": "/users/{user_id}",
                "search": "/users/search?name={name}",
                "login": "POST /users/login",
                "create": "POST /users"
            },
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        client = get_client()
        client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


