from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import transactions, discovery, semantic

app = FastAPI(title="Yelp Distributed App")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(transactions.router, tags=["Transactions"])
app.include_router(discovery.router, tags=["Discovery"])
app.include_router(semantic.router, tags=["Semantic Search"])

@app.get("/")
def root():
    return {"message": "Yelp Distributed System API is running"}
