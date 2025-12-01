import pandas as pd
from pymongo import MongoClient
import sys

# --- 1. Create the Business Lookup Map ---
print("Loading business data to create lookup map...")
try:
    df_biz = pd.read_json(
        './yelp_dataset/yelp_academic_dataset_business.json', 
        lines=True
    )
    
    # Drop businesses with no location data
    df_biz = df_biz.dropna(subset=['latitude', 'longitude', 'state'])
    
    # Create the GeoJSON 'location' field
    df_biz['location'] = df_biz.apply(
        lambda row: {
            "type": "Point",
            "coordinates": [row['longitude'], row['latitude']]
        },
        axis=1
    )
    
    # Create the map: 'business_id' -> {'state': 'AZ', 'location': {...}}
    biz_map = df_biz.set_index('business_id')[['state', 'location']].to_dict('index')
    
    print(f"Business map created with {len(biz_map)} entries.")

except Exception as e:
    print(f"Error loading business JSON: {e}")
    sys.exit()

# --- 2. Connect to MongoDB Router ---
CONNECTION_STRING = "mongodb://localhost:27017/"
try:
    client = MongoClient(CONNECTION_STRING)
    client.admin.command('ping')
    db = client['yelp_data']
    reviews_collection = db['reviews']
    
    # Get existing review_ids in batches to avoid 16MB limit
    print("Loading existing review_ids (this may take a moment)...")
    existing_review_ids = set()
    batch_size = 100000
    cursor = reviews_collection.find({}, {"review_id": 1}).batch_size(batch_size)
    
    for doc in cursor:
        if 'review_id' in doc:
            existing_review_ids.add(doc['review_id'])
    
    print(f"Connected to MongoDB. Found {len(existing_review_ids)} existing reviews.")
    print("Will skip already inserted reviews and continue from where we left off.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit()

# --- 3. Stream, Enrich, and Insert Reviews ---
review_file_path = './yelp_dataset/yelp_academic_dataset_review.json'
chunk_size = 50000  # Process 50,000 reviews at a time
total_inserted = 0

print(f"Starting review insertion from {review_file_path}...")

try:
    with pd.read_json(review_file_path, lines=True, chunksize=chunk_size) as reader:
        for chunk_df in reader:
            # --- This is the ENRICHMENT step ---
            
            # 1. Map 'state' from the biz_map
            chunk_df['state'] = chunk_df['business_id'].map(
                lambda x: biz_map.get(x, {}).get('state')
            )
            
            # 2. Map 'location' from the biz_map
            chunk_df['location'] = chunk_df['business_id'].map(
                lambda x: biz_map.get(x, {}).get('location')
            )
            
            # 3. Drop reviews for businesses we couldn't find (e.g., no state)
            chunk_df = chunk_df.dropna(subset=['state'])
            
            if chunk_df.empty:
                print("  Skipped chunk (no matching businesses).")
                continue
            
            # 4. Filter out reviews that already exist
            chunk_df = chunk_df[~chunk_df['review_id'].isin(existing_review_ids)]
            
            if chunk_df.empty:
                print("  Skipped chunk (all reviews already inserted).")
                continue
                
            # 5. Convert to dict and insert
            records_to_insert = chunk_df.to_dict('records')
            reviews_collection.insert_many(records_to_insert)
            
            # Update the set of existing review_ids for next chunk
            new_review_ids = set(chunk_df['review_id'].tolist())
            existing_review_ids.update(new_review_ids)
            
            total_inserted += len(records_to_insert)
            print(f"  Inserted {len(records_to_insert)} new records. Total: {total_inserted}")

except Exception as e:
    print(f"Error reading or inserting reviews: {e}")
finally:
    client.close()
    print(f"\nInsertion complete. Total {total_inserted} reviews inserted.")

