
from pymongo import MongoClient, WriteConcern
import json
import sys
from pathlib import Path

MONGO_URI = "mongodb://localhost:27018"
DATABASE_NAME = "yelp_data"
COLLECTION_NAME = "users"

write_concern = WriteConcern(w="majority")

def insert_users():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME].with_options(write_concern=write_concern)
    
    data_file = Path(__file__).parent / "data" / "user.subset.with_passwords.json"
    
    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        sys.exit(1)
    
    print(f"Reading users from {data_file}...")
    
    print("Clearing existing users collection...")
    deleted_count = collection.delete_many({}).deleted_count
    print(f"  Deleted {deleted_count} existing users")
    
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
                    user = json.loads(line)
                    batch.append(user)
                    
                    if len(batch) >= batch_size:
                        try:
                            collection.insert_many(batch, ordered=False)
                            processed += len(batch)
                            print(f"  Processed {processed} users...", end='\r')
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
        
        print(f"\nInsertion complete. Total users inserted: {processed}")
        
        print("Creating indexes...")
        try:
            collection.create_index([("user_id", 1)], unique=True)
            collection.create_index([("name", "text")])
            print("Indexes created successfully.")
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
        
        count = collection.count_documents({})
        print(f"Final count in database: {count}")
        
        sample = collection.find_one({"password": {"$exists": True}})
        if sample:
            print("Verified: Users have password field.")
        else:
            print("Warning: No users found with password field.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    insert_users()

