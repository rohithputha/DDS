from pymongo import MongoClient, ReadPreference, WriteConcern

# Connect to the MONGOS router, not a specific shard
MONGO_URI = "mongodb://localhost:27017" 

client = MongoClient(MONGO_URI)

# Database Configuration per Report Section 2.3
db = client.get_database("yelp_data")

# Writes: "majority" for durability
write_concern = WriteConcern(w="majority", j=True)
db_write = db.with_options(write_concern=write_concern)

# Reads: "secondaryPreferred" for read scaling
read_preference = ReadPreference.SECONDARY_PREFERRED
db_read = db.with_options(read_preference=read_preference)

# Users Service Connection (Port 27018)
MONGO_USERS_URI = "mongodb://localhost:27018"
client_users = MongoClient(MONGO_USERS_URI)
db_users = client_users.get_database("yelp_data")
