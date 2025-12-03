from pymongo import MongoClient
import sys

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)

source_db = client['test']
target_db = client['yelp_data']

def migrate_collection(coll_name):
    source_coll = source_db[coll_name]
    target_coll = target_db[coll_name]
    
    count = source_coll.count_documents({})
    if count == 0:
        print(f"No data in test.{coll_name}")
        return

    print(f"Migrating {count} documents from test.{coll_name} to yelp_data.{coll_name}...")
    
    batch_size = 1000
    batch = []
    processed = 0
    
    cursor = source_coll.find({})
    for doc in cursor:
        batch.append(doc)
        if len(batch) >= batch_size:
            try:
                target_coll.insert_many(batch, ordered=False)
            except Exception as e:
                print(f"Error inserting batch: {e}")
            processed += len(batch)
            print(f"Processed {processed}/{count}", end='\r')
            batch = []
            
    if batch:
        try:
            target_coll.insert_many(batch, ordered=False)
        except Exception as e:
            print(f"Error inserting final batch: {e}")
        processed += len(batch)
        
    print(f"\nMigration of {coll_name} complete.")

if __name__ == "__main__":
    print("Starting migration...")
    migrate_collection('businesses')
    migrate_collection('reviews')
    migrate_collection('users') 
    print("Migration finished.")
