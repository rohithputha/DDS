# FastAPI Backend for Yelp Dataset

REST API backend for the geo-distributed Yelp dataset application.

## Setup

Install dependencies:

```bash
cd DDS
source ../venv/bin/activate
pip install -r requirements.txt
```

Make sure MongoDB cluster is running:

```bash
docker-compose up -d
```

## Running the Server

```bash
cd DDS
source ../venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running:

- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## Endpoints

### Health Check

- `GET /health` - Check API and database connectivity

### Businesses

- `GET /businesses/search/location?latitude={lat}&longitude={lon}&radius={km}` - Search by location
- `GET /businesses/search/region?state={state}&city={city}&category={cat}` - Search by region
- `GET /businesses/{business_id}` - Get business by ID
- `POST /businesses` - Create new business

### Reviews

- `GET /reviews/business/{business_id}?limit={n}&offset={m}` - Get reviews for a business
- `POST /reviews` - Create new review (with transaction to update business aggregates)

### Users

- `GET /users/{user_id}` - Get user by ID
- `GET /users/search?name={name}` - Search users by name
- `POST /users` - Create new user

## Features

- Shard routing: Businesses and reviews are automatically routed to correct shards based on state
- Replication: Reads from secondary replicas, writes with majority concern
- Transactions: Review creation uses transactions to atomically update business aggregates
- Distributed joins: Review queries use $lookup for distributed joins with users collection
- Geospatial queries: Location-based searches use MongoDB's 2dsphere index

## Example Requests

Search businesses by location:

```bash
curl "http://localhost:8000/businesses/search/location?latitude=34.0522&longitude=-118.2437&radius=5&limit=10"
```

Search businesses by region:

```bash
curl "http://localhost:8000/businesses/search/region?state=CA&city=Los%20Angeles&limit=20"
```

Get reviews for a business:

```bash
curl "http://localhost:8000/reviews/business/{business_id}?limit=50"
```

Create a review:

```bash
curl -X POST "http://localhost:8000/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "abc123",
    "user_id": "user456",
    "stars": 5,
    "text": "Great place!",
    "useful": 0,
    "funny": 0,
    "cool": 0
  }'
```

## Testing

See [TESTING.md](TESTING.md) for detailed testing instructions including:

- Interactive API documentation (Swagger UI)
- curl command examples
- Python requests examples
- Postman/Insomnia setup
