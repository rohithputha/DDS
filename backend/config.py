"""
Configuration settings for MongoDB connection and shard routing.
"""
from pymongo import ReadPreference, WriteConcern

MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "yelp_data"

# Read from secondary replicas when available for better read performance
READ_PREFERENCE = ReadPreference.SECONDARY_PREFERRED
# Write to majority of replicas for durability
WRITE_CONCERN = WriteConcern(w="majority")

# Maps US states to regions for shard routing
STATE_TO_REGION = {
    # PACIFIC
    "CA": "PACIFIC",
    "NV": "PACIFIC",
    "OR": "PACIFIC",
    "WA": "PACIFIC",
    # MOUNTAIN
    "AZ": "MOUNTAIN",
    "CO": "MOUNTAIN",
    "ID": "MOUNTAIN",
    "MT": "MOUNTAIN",
    "NM": "MOUNTAIN",
    "UT": "MOUNTAIN",
    "WY": "MOUNTAIN",
    # CENTRAL
    "IL": "CENTRAL",
    "IN": "CENTRAL",
    "LA": "CENTRAL",
    "MO": "CENTRAL",
    "TN": "CENTRAL",
    "TX": "CENTRAL",
    # EASTERN
    "DE": "EASTERN",
    "FL": "EASTERN",
    "GA": "EASTERN",
    "MA": "EASTERN",
    "NC": "EASTERN",
    "NJ": "EASTERN",
    "NY": "EASTERN",
    "OH": "EASTERN",
    "PA": "EASTERN",
    "SC": "EASTERN",
    "VA": "EASTERN",
    # OTHER
    "AB": "OTHER",
    "ON": "OTHER",
    "QC": "OTHER",
    "WI": "OTHER",
    "HI": "OTHER",
}

VALID_STATES = set(STATE_TO_REGION.keys())

