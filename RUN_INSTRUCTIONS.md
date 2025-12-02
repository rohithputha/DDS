# How to Run the Application

## Prerequisites
- Docker and Docker Compose installed and running
- Python 3.8+ with virtual environment
- Node.js and npm installed

## Step 1: Start MongoDB Clusters and Services

### Start Main Cluster (Businesses/Reviews) and Vector Services
```bash
cd /Users/sarathkumardunga/Desktop/DDS512/DDS
docker-compose up -d
```

Wait for containers to start (about 30 seconds), then initialize the cluster:
```bash
bash init_main_cluster.sh
```

### Start Users Cluster
```bash
cd users-docker
docker-compose -f docker-compose-users.yml up -d
cd ..
```

Wait for containers to start (about 30 seconds), then initialize:
```bash
bash init_users_db.sh
```

### Verify All Containers Are Running
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "mongo|weaviate|ollama"
```

You should see:
- mongo-router (main cluster)
- mongo-configsvr-1, mongo-configsvr-2, mongo-configsvr-3
- mongo-shard-a-1 through mongo-shard-e-3 (15 containers)
- user-mongo-router (users cluster)
- user-mongo-configsvr-1 through user-mongo-configsvr-3
- user-mongo-shard-*-replica-* (9 containers)
- dds-weaviate-1
- dds-ollama-1

## Step 2: Load Data (If Not Already Loaded)

If you haven't loaded the subset data yet:
```bash
cd /Users/sarathkumardunga/Desktop/DDS512/DDS
source ../venv/bin/activate
python3 insert_businesses.py
python3 insert_reviews.py
python3 insert_users.py
```

Or run the complete setup script:
```bash
bash setup_data.sh
```

## Step 3: Start Backend Server

```bash
cd /Users/sarathkumardunga/Desktop/DDS512/DDS
source ../venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Step 4: Start Frontend Server

Open a new terminal window:

```bash
cd /Users/sarathkumardunga/Desktop/DDS512/DDS/frontend
npm run dev
```

The frontend will be available at:
- http://localhost:5173

## Step 5: Test the Application

### 1. Login
- Open http://localhost:5173 in your browser
- You'll see the login page
- Use credentials from `data/user.subset.with_passwords.json`
  - Example: Find a user_id and password from that file
  - Or check the file: `head -5 data/user.subset.with_passwords.json`

### 2. Search for Businesses
- After login, you'll see the search interface
- Enter latitude and longitude (e.g., 34.0522, -118.2437 for Los Angeles)
- Set radius (default 5km)
- Click "Search" or use semantic search

### 3. View Business Details
- Click on a business from the results
- You'll see business details and existing reviews

### 4. Write a Review
- Scroll to the "Write a Review" section
- Enter rating (1-5 stars)
- Write your review text
- Click "Submit Review"
- The review should appear in the list
- Business aggregates (stars, review_count) should update
- Your user's review_count should update

## Troubleshooting

### Backend Won't Start
- Check if port 8000 is already in use: `lsof -i :8000`
- Kill the process if needed: `kill <PID>`
- Or use a different port: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001`

### Frontend Won't Start
- Check if port 5173 is already in use: `lsof -i :5173`
- Install dependencies: `npm install`

### MongoDB Connection Errors
- Verify containers are running: `docker ps`
- Check container logs: `docker logs mongo-router`
- Wait longer for initialization (replica sets need time to stabilize)

### Login Fails
- Verify users data is loaded: 
  ```bash
  docker exec user-mongo-router mongosh --port 27017 --eval "use yelp_data; db.users.countDocuments({})"
  ```
- Check if user has password field:
  ```bash
  docker exec user-mongo-router mongosh --port 27017 --eval "use yelp_data; db.users.findOne({'password': {\$exists: true}})"
  ```

### Review Creation Fails
- Check backend logs for error messages
- Verify business exists: `curl http://localhost:8000/businesses/{business_id}`
- Verify user exists in users cluster
- Check MongoDB logs: `docker logs mongo-router`

## Quick Verification Commands

```bash
# Check businesses count
docker exec mongo-router mongosh --eval "use yelp_data; db.businesses.countDocuments({})"

# Check reviews count
docker exec mongo-router mongosh --eval "use yelp_data; db.reviews.countDocuments({})"

# Check users count
docker exec user-mongo-router mongosh --port 27017 --eval "use yelp_data; db.users.countDocuments({})"

# Check users with passwords
docker exec user-mongo-router mongosh --port 27017 --eval "use yelp_data; db.users.countDocuments({'password': {\$exists: true}})"
```

## Stopping the Application

```bash
# Stop frontend (Ctrl+C in frontend terminal)
# Stop backend (Ctrl+C in backend terminal)

# Stop Docker containers
cd /Users/sarathkumardunga/Desktop/DDS512/DDS
docker-compose down
cd users-docker
docker-compose -f docker-compose-users.yml down
cd ..
```

## Notes

- The backend auto-reloads on code changes (--reload flag)
- Frontend hot-reloads on code changes (Vite default)
- Authentication tokens are stored in browser localStorage
- Sessions expire after 24 hours
- Review updates to user review_count use eventual consistency (may take a moment)

