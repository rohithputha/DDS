# Testing the API Endpoints

This guide covers multiple ways to test the FastAPI endpoints.

## Prerequisites

1. Start the MongoDB cluster:

```bash
cd DDS
docker-compose up -d
```

2. Start the FastAPI server:

```bash
cd DDS
source ../venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## Method 1: Interactive API Documentation (Easiest)

FastAPI automatically generates interactive API documentation:

1. Open your browser and go to: **http://localhost:8000/docs**
2. You'll see the Swagger UI with all endpoints
3. Click on any endpoint to expand it
4. Click "Try it out" to test the endpoint
5. Fill in the parameters and click "Execute"

This is the easiest way to test endpoints without writing any code.

## Method 2: Using curl Commands

### Health Check

```bash
curl http://localhost:8000/health
```

### Search Businesses by Location

```bash
# Search near Los Angeles (latitude 34.0522, longitude -118.2437)
curl "http://localhost:8000/businesses/search/location?latitude=34.0522&longitude=-118.2437&radius=5&limit=10"
```

### Search Businesses by Region

```bash
# Search in California
curl "http://localhost:8000/businesses/search/region?state=CA&limit=20"

# Search in Los Angeles, CA
curl "http://localhost:8000/businesses/search/region?state=CA&city=Los%20Angeles&limit=20"

# Search restaurants in California
curl "http://localhost:8000/businesses/search/region?state=CA&category=Restaurants&limit=20"
```

### Get Business by ID

```bash
# Replace {business_id} with an actual business_id from your database
curl "http://localhost:8000/businesses/{business_id}"
```

### Create a New Business

```bash
curl -X POST "http://localhost:8000/businesses" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Restaurant",
    "address": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "postal_code": "90001",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "categories": "Restaurants, Food"
  }'
```

### Get Reviews for a Business

```bash
# Replace {business_id} with an actual business_id
curl "http://localhost:8000/reviews/business/{business_id}?limit=50&offset=0"
```

### Create a New Review

```bash
# Replace business_id and user_id with actual IDs from your database
curl -X POST "http://localhost:8000/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "your_business_id_here",
    "user_id": "your_user_id_here",
    "stars": 5,
    "text": "Great place! Highly recommend.",
    "useful": 0,
    "funny": 0,
    "cool": 0
  }'
```

### Get User by ID

```bash
# Replace {user_id} with an actual user_id
curl "http://localhost:8000/users/{user_id}"
```

### Search Users

```bash
curl "http://localhost:8000/users/search?name=John&limit=20"
```

### Create a New User

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "review_count": 0
  }'
```

## Method 3: Using Python requests

Create a test script `test_endpoints.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print("Health check:", response.json())

# Search businesses by location
response = requests.get(
    f"{BASE_URL}/businesses/search/location",
    params={
        "latitude": 34.0522,
        "longitude": -118.2437,
        "radius": 5,
        "limit": 10
    }
)
print("\nBusinesses near LA:", len(response.json()), "results")

# Search businesses by region
response = requests.get(
    f"{BASE_URL}/businesses/search/region",
    params={
        "state": "CA",
        "city": "Los Angeles",
        "limit": 20
    }
)
print("\nBusinesses in LA:", len(response.json()), "results")

# Get first business ID if available
if response.json():
    business_id = response.json()[0].get("business_id")

    # Get reviews for that business
    reviews_response = requests.get(
        f"{BASE_URL}/reviews/business/{business_id}",
        params={"limit": 10}
    )
    print(f"\nReviews for business {business_id}:", len(reviews_response.json()), "results")
```

Run it:

```bash
cd DDS
source ../venv/bin/activate
pip install requests
python test_endpoints.py
```

## Method 4: Using Postman or Insomnia

1. Import the OpenAPI schema:

   - Go to http://localhost:8000/openapi.json
   - Copy the JSON
   - Import it into Postman/Insomnia

2. Or manually create requests:
   - Base URL: `http://localhost:8000`
   - Use the endpoints listed in the README

## Method 5: Get Sample Data IDs

To get actual IDs from your database for testing:

```bash
# Connect to MongoDB router
docker exec -it mongo-router mongosh

# In mongosh:
use yelp_data

# Get a sample business
db.businesses.findOne({}, {business_id: 1, name: 1, state: 1, city: 1})

# Get a sample review
db.reviews.findOne({}, {review_id: 1, business_id: 1, user_id: 1})

# Get a sample user
db.users.findOne({}, {user_id: 1, name: 1})
```

## Testing Tips

1. **Start with the health endpoint** to verify the server is running
2. **Use the Swagger UI** (http://localhost:8000/docs) for the easiest testing experience
3. **Check the response status codes**:
   - 200: Success
   - 201: Created
   - 400: Bad Request (invalid parameters)
   - 404: Not Found
   - 500: Server Error
4. **View response in JSON format** by adding `| python -m json.tool` to curl commands:
   ```bash
   curl "http://localhost:8000/businesses/search/region?state=CA" | python -m json.tool
   ```

## Common Issues

- **Connection refused**: Make sure the server is running on port 8000
- **Database connection errors**: Verify MongoDB cluster is running with `docker-compose ps`
- **Empty results**: Check if data was inserted correctly into the database
- **404 errors**: Verify the IDs you're using exist in the database
