"""
MongoDB database connection and collection utilities.
"""
from pymongo import MongoClient, ReadPreference, WriteConcern
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
from .config import (
    MONGODB_CONNECTION_STRING,
    DATABASE_NAME,
    READ_PREFERENCE,
    WRITE_CONCERN
)

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Get or create MongoDB client with connection pooling."""
    global _client
    if _client is None:
        _client = MongoClient(
            MONGODB_CONNECTION_STRING,
            maxPoolSize=50,
            minPoolSize=10
        )
    return _client


def get_database() -> Database:
    """Get the yelp_data database."""
    client = get_client()
    return client[DATABASE_NAME]


def get_collection(collection_name: str, read_preference: ReadPreference = None, 
                   write_concern: WriteConcern = None) -> Collection:
    """
    Get a collection with read/write preferences applied.
    
    If preferences are not specified, uses defaults from config.
    """
    db = get_database()
    collection = db[collection_name]
    
    if read_preference is not None:
        collection = collection.with_options(read_preference=read_preference)
    else:
        collection = collection.with_options(read_preference=READ_PREFERENCE)
    
    if write_concern is not None:
        collection = collection.with_options(write_concern=write_concern)
    else:
        collection = collection.with_options(write_concern=WRITE_CONCERN)
    
    return collection


def close_connection():
    """Close the MongoDB connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None

