import pandas as pd
from pymongo import MongoClient
import sys

# --- 1. Load your DataFrame ---
try:
    df = pd.read_json(
        './yelp_dataset/yelp_academic_dataset_business.json', 
        lines=True
    )
    print(f"Successfully loaded {len(df)} total businesses.")
except Exception as e:
    print(f"Error reading JSON file: {e}")
    sys.exit()

# --- 2. Prepare Data for MongoDB ---
print("Preparing data for insertion...")

# Drop businesses that have missing lat/long or state
df = df.dropna(subset=['latitude', 'longitude', 'state'])

# Create the 'location' field in GeoJSON format
# IMPORTANT: Coordinates are [longitude, latitude]
df['location'] = df.apply(
    lambda row: {
        "type": "Point",
        "coordinates": [row['longitude'], row['latitude']]
    },
    axis=1
)
print(f"Data prepared. {len(df)} valid businesses to insert.")


# --- 3. Connect to the MongoDB Router ---
# This is the ONLY connection string you need.
# It connects to the 'mongo-router' container's exposed port.
CONNECTION_STRING = "mongodb://localhost:27017/"

try:
    client = MongoClient(CONNECTION_STRING)
    client.admin.command('ping')
    print("MongoDB router connection successful.")
except Exception as e:
    print(f"Error connecting to MongoDB router: {e}")
    sys.exit()

# Define your database and collection
# FIXED: Use 'yelp_data' database instead of 'test'
db = client['yelp_data']
collection = db['businesses']

# --- 4. Insert the Data ---
# Convert the DataFrame to a list of dictionaries
records_to_insert = df.to_dict('records')

if not records_to_insert:
    print("No records to insert.")
    sys.exit()

print(f"Inserting {len(records_to_insert)} records into 'yelp_data.businesses'...")

try:
    # Clear the collection for a fresh run (optional)
    collection.delete_many({})
    
    # Insert all records
    result = collection.insert_many(records_to_insert)
    print(f"  SUCCESS: Inserted {len(result.inserted_ids)} records.")
    print("  MongoDB is automatically partitioning this data across your 5 shards!")
    
except Exception as e:
    print(f"  FAILED to insert records: {e}")

finally:
    client.close()
    print("Connection closed.")

