
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
import time
from fastapi.middleware.cors import CORSMiddleware

from .database import get_client, close_connection
from .routers import businesses, reviews, users, discovery, semantic


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        client = get_client()
        client.admin.command('ping')
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection warning: {e}")
    
    yield
    
    close_connection()
    print("MongoDB connection closed")


app = FastAPI(
    title="Yelp Dataset API",
    description="REST API for geo-distributed local discovery on Yelp dataset",
    version="1.0.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.url.path} | Start: {start_time} | End: {time.time()} | Duration: {process_time}s")
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(businesses.router)
app.include_router(reviews.router)
app.include_router(users.router)


app.include_router(discovery.router)

# - /search/semantic
app.include_router(semantic.router)


@app.get("/")
async def root():
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


