#!/bin/bash

# 1. Initiate Config Server Replica Set
echo "Initiating Config Server Replica Set..."
docker exec user-mongo-configsvr-1 mongosh --port 27017 --eval '
  rs.initiate({
    _id: "rs-user-config",
    configsvr: true,
    members: [
      { _id: 0, host: "user-mongo-configsvr-1:27017" },
      { _id: 1, host: "user-mongo-configsvr-2:27017" },
      { _id: 2, host: "user-mongo-configsvr-3:27017" }
    ]
  })
'

# 2. Initiate Shard 1 Replica Set
echo "Initiating Shard 1 Replica Set..."
docker exec user-mongo-shard-1-replica-1 mongosh --port 27017 --eval '
  rs.initiate({
    _id: "rs-user-shard-1",
    members: [
      { _id: 0, host: "user-mongo-shard-1-replica-1:27017" },
      { _id: 1, host: "user-mongo-shard-1-replica-2:27017" },
      { _id: 2, host: "user-mongo-shard-1-replica-3:27017" }
    ]
  })
'

# 3. Initiate Shard 2 Replica Set
echo "Initiating Shard 2 Replica Set..."
docker exec user-mongo-shard-2-replica-1 mongosh --port 27017 --eval '
  rs.initiate({
    _id: "rs-user-shard-2",
    members: [
      { _id: 0, host: "user-mongo-shard-2-replica-1:27017" },
      { _id: 1, host: "user-mongo-shard-2-replica-2:27017" },
      { _id: 2, host: "user-mongo-shard-2-replica-3:27017" }
    ]
  })
'

# 4. Initiate Shard 3 Replica Set
echo "Initiating Shard 3 Replica Set..."
docker exec user-mongo-shard-3-replica-1 mongosh --port 27017 --eval '
  rs.initiate({
    _id: "rs-user-shard-3",
    members: [
      { _id: 0, host: "user-mongo-shard-3-replica-1:27017" },
      { _id: 1, host: "user-mongo-shard-3-replica-2:27017" },
      { _id: 2, host: "user-mongo-shard-3-replica-3:27017" }
    ]
  })
'

# Wait for replica sets to stabilize
echo "Waiting for replica sets to stabilize..."
sleep 15

# 5. Add Shards to Router
echo "Adding Shards to Router..."
docker exec user-mongo-router mongosh --port 27017 --eval '
  sh.addShard("rs-user-shard-1/user-mongo-shard-1-replica-1:27017,user-mongo-shard-1-replica-2:27017,user-mongo-shard-1-replica-3:27017");
  sh.addShard("rs-user-shard-2/user-mongo-shard-2-replica-1:27017,user-mongo-shard-2-replica-2:27017,user-mongo-shard-2-replica-3:27017");
  sh.addShard("rs-user-shard-3/user-mongo-shard-3-replica-1:27017,user-mongo-shard-3-replica-2:27017,user-mongo-shard-3-replica-3:27017");
'

echo "Initialization Complete!"
