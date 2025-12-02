#!/bin/bash

# Master script to set up and populate all MongoDB clusters with subset data
# Shows progress at each step

set -e

echo "=========================================="
echo "MongoDB Data Setup Script"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Stop and clean everything
echo "[STEP 1/8] Stopping and cleaning existing containers..."
docker-compose down -v 2>/dev/null || true
cd users-docker
docker-compose -f docker-compose-users.yml down -v 2>/dev/null || true
cd ..
echo "✓ Cleaned up existing containers and volumes"
echo ""

# Step 2: Start DDS cluster (businesses/reviews)
echo "[STEP 2/8] Starting DDS cluster (businesses/reviews)..."
docker-compose up -d
echo "✓ DDS cluster containers started"
echo "  Waiting for containers to initialize..."
sleep 35
echo ""

# Step 3: Initialize main cluster replica sets and sharding
echo "[STEP 3/8] Initializing main cluster replica sets and sharding..."
bash init_main_cluster.sh
echo ""

# Step 4: Start users cluster
echo "[STEP 4/8] Starting users cluster..."
cd users-docker
docker-compose -f docker-compose-users.yml up -d
echo "✓ Users cluster containers started"
echo "  Waiting for containers to initialize..."
sleep 35
cd ..
echo ""

# Step 5: Initialize users cluster replica sets
echo "[STEP 5/8] Initializing users cluster replica sets..."
bash init_users_db.sh
echo ""

# Step 6: Insert businesses
echo "[STEP 6/8] Inserting businesses from data/business.subset.json..."
source ../venv/bin/activate
python3 insert_businesses.py
echo ""

# Step 7: Insert reviews
echo "[STEP 7/8] Inserting reviews from data/review.subset.json..."
python3 insert_reviews.py
echo ""

# Step 8: Insert users
echo "[STEP 8/8] Inserting users from data/user.subset.with_passwords.json..."
python3 insert_users.py
echo ""

# Verification
echo "=========================================="
echo "Data setup complete!"
echo "=========================================="
echo ""
echo "Verifying data counts..."
echo ""

BUSINESS_COUNT=$(docker exec mongo-router mongosh --quiet --eval "use yelp_data; db.businesses.countDocuments({})" 2>/dev/null || echo "0")
REVIEW_COUNT=$(docker exec mongo-router mongosh --quiet --eval "use yelp_data; db.reviews.countDocuments({})" 2>/dev/null || echo "0")
USER_COUNT=$(docker exec user-mongo-router mongosh --port 27017 --quiet --eval "use yelp_data; db.users.countDocuments({})" 2>/dev/null || echo "0")
USER_WITH_PASSWORD=$(docker exec user-mongo-router mongosh --port 27017 --quiet --eval "use yelp_data; db.users.countDocuments({'password': {\$exists: true}})" 2>/dev/null || echo "0")

echo "Businesses: $BUSINESS_COUNT"
echo "Reviews: $REVIEW_COUNT"
echo "Users: $USER_COUNT"
echo "Users with passwords: $USER_WITH_PASSWORD"
echo ""

if [ "$USER_WITH_PASSWORD" -gt 0 ]; then
    echo "✓ Users have password field"
else
    echo "⚠ Warning: No users found with password field"
fi

echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo "  - Businesses cluster: mongodb://localhost:27017"
echo "  - Users cluster: mongodb://localhost:27018"
echo "  - Weaviate: http://localhost:8080"
echo "  - Ollama: http://localhost:11434"
echo ""
echo "You can now start the backend:"
echo "  cd $SCRIPT_DIR"
echo "  source ../venv/bin/activate"
echo "  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
