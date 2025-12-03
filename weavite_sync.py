import weaviate
from pymongo import MongoClient
import ollama
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"



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
        if not w_client.collections.exists("Review"):
            from weaviate.classes.config import Configure
            w_client.collections.create(
                "Review",
                vectorizer_config=Configure.Vectorizer.none()
            )
            
        reviews_collection = w_client.collections.get("Review")

        with db.watch() as stream:
            for change in stream:
                print(f"Received change: {change['operationType']} on {change['ns']}")
                if change["operationType"] == "insert" and change["ns"]["coll"] == "reviews":
                    doc = change["fullDocument"]
                    
                    review_text = doc.get("text", "")
                    try:
                        response = ollama.embed(model='all-minilm', input=review_text)
                        vector = response['embeddings'][0]
                    except Exception as e:
                        print(f"Error generating embedding with Ollama: {e}")
                        continue
                    
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