import weaviate
from pymongo import MongoClient
import ollama
import os
import time

def backfill_reviews():
    print("Connecting to MongoDB...")
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.yelp_data
    reviews_collection = db.reviews

    print("Connecting to Weaviate...")
    w_client = weaviate.connect_to_local(
        port=8080,
        grpc_port=50051, 
        headers={}
    )

    print("Using Ollama for embeddings (model: all-minilm)...")
    # Ensure user has run: ollama pull all-minilm

    try:
        # Create collection if not exists (DO NOT DELETE if resuming)
        if not w_client.collections.exists("Review"):
            from weaviate.classes.config import Configure
            w_client.collections.create(
                "Review",
                vectorizer_config=Configure.Vectorizer.none()
            )
            print("Created 'Review' collection in Weaviate.")
        else:
            print("Collection 'Review' already exists. Checking for resume...")
        
        w_reviews = w_client.collections.get("Review")

    except Exception as e:
        print(f"Error setting up collection: {e}")
        # Fallback or exit?
        try:
            w_reviews = w_client.collections.get("Review")
        except:
            print("Critical error: Could not access 'Review' collection.")
            return

    # Check existing count to RESUME
    try:
        current_count = w_reviews.aggregate.over_all(total_count=True).total_count
        print(f"Current Weaviate count: {current_count}")
    except:
        current_count = 0

    total_reviews = reviews_collection.count_documents({})
    print(f"Found {total_reviews} reviews in MongoDB.")

    print(f"Found {total_reviews} reviews in MongoDB.")
    
    if current_count > 0:
        print(f"Resuming backfill... Skipping first {current_count} reviews.")
    
    # Skip existing
    cursor = reviews_collection.find({}).skip(current_count)
    
    batch_size = 10 # Drastically reduced batch size
    processed = current_count

    print("Starting backfill with batching...")
    start_time = time.time()
    
    batch_docs = []
    
    with w_reviews.batch.dynamic() as batch:
        for doc in cursor:
            review_text = doc.get("text", "")
            if not review_text:
                continue
            
            batch_docs.append(doc)
            
            if len(batch_docs) >= batch_size:
                texts = [d["text"] for d in batch_docs]
                
                try:
                    # Ollama embed API
                    response = ollama.embed(model='all-minilm', input=texts)
                    vectors = response['embeddings']
                    
                    for i, d in enumerate(batch_docs):
                        batch.add_object(
                            properties={
                                "review_id": str(d["_id"]),
                                "business_id": d["business_id"],
                                "text": d["text"]
                            },
                            vector=vectors[i]
                        )
                    
                    processed += len(batch_docs)
                    batch_docs = []
                    print(f"Processed {processed}/{total_reviews} reviews...", end='\r')
                    
                    # Rate limiting to let Weaviate catch up/flush
                    time.sleep(0.5) 
                    
                except Exception as e:
                    print(f"\nError generating embeddings with Ollama: {e}")
                    # If error, try to continue with next batch? Or stop?
                    # Let's stop to avoid skipping data without inserting
                    return

        # Process remaining
        if batch_docs:
            texts = [d["text"] for d in batch_docs]
            try:
                response = ollama.embed(model='all-minilm', input=texts)
                vectors = response['embeddings']
                for i, d in enumerate(batch_docs):
                    batch.add_object(
                        properties={
                            "review_id": str(d["_id"]),
                            "business_id": d["business_id"],
                            "text": d["text"]
                        },
                        vector=vectors[i]
                    )
                processed += len(batch_docs)
            except Exception as e:
                print(f"Error generating embeddings: {e}")

        print(f"\nBackfill complete! Processed {processed} reviews.")

        # Verification
        print("\nVerifying Weaviate count...")
        count = w_reviews.aggregate.over_all(total_count=True).total_count
        print(f"Total objects in Weaviate 'Review' collection: {count}")

    w_client.close()
    mongo_client.close()

if __name__ == "__main__":
    backfill_reviews()
