import weaviate
from pymongo import MongoClient
import ollama
import os

# Fix for segmentation fault in threaded environment
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Setup Weaviate Client (v4)
# w_client = weaviate.connect_to_local(...)

# model = SentenceTransformer('all-MiniLM-L6-v2') 

# mongo_client = MongoClient("mongodb://localhost:27017")
# db = mongo_client.yelp_data

def process_change_stream():
    print("Initializing clients in background thread...")
    
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.yelp_data
    
    w_client = weaviate.connect_to_local(
        port=8080,
        grpc_port=50051, 
        headers={}
    )
    
    print("Using Ollama for embeddings (model: all-minilm)...")
    print("Listening for changes in Reviews...")
    try:
        # Create collection if not exists
        if not w_client.collections.exists("Review"):
            from weaviate.classes.config import Configure
            w_client.collections.create(
                "Review",
                vectorizer_config=Configure.Vectorizer.none()
            )
            
        reviews_collection = w_client.collections.get("Review")

        # Watch the database
        with db.watch() as stream:
            for change in stream:
                print(f"Received change: {change['operationType']} on {change['ns']}")
                if change["operationType"] == "insert" and change["ns"]["coll"] == "reviews":
                    doc = change["fullDocument"]
                    
                    # 1. Generate Embedding
                    review_text = doc.get("text", "")
                    try:
                        response = ollama.embed(model='all-minilm', input=review_text)
                        vector = response['embeddings'][0]
                    except Exception as e:
                        print(f"Error generating embedding with Ollama: {e}")
                        continue
                    
                    # 2. Push to Weaviate 
                    reviews_collection.data.insert(
                        properties={
                            "review_id": str(doc["_id"]),
                            "business_id": doc["business_id"],
                            "text": review_text
                        },
                        vector=vector
                    )
                    print(f"Indexed review {doc['_id']}")
    except Exception as e:
        print(f"Error in sync worker: {e}")
    finally:
        w_client.close()

if __name__ == "__main__":
    process_change_stream()