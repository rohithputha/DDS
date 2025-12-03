
from pymongo import MongoClient, WriteConcern
import json
import sys
from pathlib import Path

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "yelp_data"
COLLECTION_NAME = "businesses"

write_concern = WriteConcern(w="majority")

def insert_businesses():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME].with_options(write_concern=write_concern)
    
    data_file = Path(__file__).parent / "data" / "business.subset.json"
    
    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        sys.exit(1)
    
    print(f"Reading businesses from {data_file}...")
    
    print("Clearing existing businesses collection...")
    deleted_count = collection.delete_many({}).deleted_count
    print(f"  Deleted {deleted_count} existing businesses")
    
    batch_size = 1000
    batch = []
    processed = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    business = json.loads(line)
                    
                    if 'latitude' in business and 'longitude' in business:
                        business['location'] = {
                            'type': 'Point',
                            'coordinates': [business['longitude'], business['latitude']]
                        }
                    
                    batch.append(business)
                    
                    if len(batch) >= batch_size:
                        try:
                            collection.insert_many(batch, ordered=False)
                            processed += len(batch)
                            print(f"  Processed {processed} businesses...", end='\r')
                            sys.stdout.flush()
                            batch = []
                        except Exception as e:
                            print(f"\nError inserting batch: {e}")
                            batch = []
                            
                except json.JSONDecodeError as e:
                    print(f"\nError parsing line {line_num}: {e}")
                    continue
            
            if batch:
                try:
                    collection.insert_many(batch, ordered=False)
                    processed += len(batch)
                except Exception as e:
                    print(f"\nError inserting final batch: {e}")
        
        print(f"\nInsertion complete. Total businesses inserted: {processed}")
        
        print("Creating geospatial index on location field...")
        try:
            collection.create_index([("location", "2dsphere")])
            print("Geospatial index created successfully.")
        except Exception as e:
            print(f"Warning: Could not create geospatial index: {e}")
        
        count = collection.count_documents({})
        print(f"Final count in database: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    insert_businesses()

