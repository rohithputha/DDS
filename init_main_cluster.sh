#!/bin/bash


set -e

echo "=========================================="
echo "Initializing Main MongoDB Cluster"
echo "=========================================="
echo ""

echo "[1/7] Initiating Config Server Replica Set..."
docker exec mongo-configsvr-1 mongosh --eval "
rs.initiate({
  _id: 'rs-config',
  configsvr: true,
  members: [
    { _id: 0, host: 'mongo-configsvr-1:27017' },
    { _id: 1, host: 'mongo-configsvr-2:27017' },
    { _id: 2, host: 'mongo-configsvr-3:27017' }
  ]
})
" --quiet
echo "✓ Config server replica set initiated"
echo ""

echo "[2/7] Initiating Shard A (PACIFIC region)..."
docker exec mongo-shard-a-1 mongosh --eval "
rs.initiate({
  _id: 'rs-shard-a',
  members: [
    { _id: 0, host: 'mongo-shard-a-1:27017' },
    { _id: 1, host: 'mongo-shard-a-2:27017' },
    { _id: 2, host: 'mongo-shard-a-3:27017' }
  ]
})
" --quiet
echo "✓ Shard A replica set initiated"
echo ""

echo "[3/7] Initiating Shard B (MOUNTAIN region)..."
docker exec mongo-shard-b-1 mongosh --eval "
rs.initiate({
  _id: 'rs-shard-b',
  members: [
    { _id: 0, host: 'mongo-shard-b-1:27017' },
    { _id: 1, host: 'mongo-shard-b-2:27017' },
    { _id: 2, host: 'mongo-shard-b-3:27017' }
  ]
})
" --quiet
echo "✓ Shard B replica set initiated"
echo ""

echo "[4/7] Initiating Shard C (CENTRAL region)..."
docker exec mongo-shard-c-1 mongosh --eval "
rs.initiate({
  _id: 'rs-shard-c',
  members: [
    { _id: 0, host: 'mongo-shard-c-1:27017' },
    { _id: 1, host: 'mongo-shard-c-2:27017' },
    { _id: 2, host: 'mongo-shard-c-3:27017' }
  ]
})
" --quiet
echo "✓ Shard C replica set initiated"
echo ""

echo "[5/7] Initiating Shard D (EASTERN region)..."
docker exec mongo-shard-d-1 mongosh --eval "
rs.initiate({
  _id: 'rs-shard-d',
  members: [
    { _id: 0, host: 'mongo-shard-d-1:27017' },
    { _id: 1, host: 'mongo-shard-d-2:27017' },
    { _id: 2, host: 'mongo-shard-d-3:27017' }
  ]
})
" --quiet
echo "✓ Shard D replica set initiated"
echo ""

echo "[6/7] Initiating Shard E (OTHER region)..."
docker exec mongo-shard-e-1 mongosh --eval "
rs.initiate({
  _id: 'rs-shard-e',
  members: [
    { _id: 0, host: 'mongo-shard-e-1:27017' },
    { _id: 1, host: 'mongo-shard-e-2:27017' },
    { _id: 2, host: 'mongo-shard-e-3:27017' }
  ]
})
" --quiet
echo "✓ Shard E replica set initiated"
echo ""

echo "Waiting for replica sets to stabilize..."
sleep 15

echo "[7/7] Configuring sharding and zone-based routing..."
docker exec mongo-router mongosh --eval "
print('Starting cluster configuration...');

// Add shards
print('Adding 5 shard replica sets...');
sh.addShard('rs-shard-a/mongo-shard-a-1:27017,mongo-shard-a-2:27017,mongo-shard-a-3:27017');
sh.addShard('rs-shard-b/mongo-shard-b-1:27017,mongo-shard-b-2:27017,mongo-shard-b-3:27017');
sh.addShard('rs-shard-c/mongo-shard-c-1:27017,mongo-shard-c-2:27017,mongo-shard-c-3:27017');
sh.addShard('rs-shard-d/mongo-shard-d-1:27017,mongo-shard-d-2:27017,mongo-shard-d-3:27017');
sh.addShard('rs-shard-e/mongo-shard-e-1:27017,mongo-shard-e-2:27017,mongo-shard-e-3:27017');

// Enable sharding
print('Enabling sharding for yelp_data database...');
sh.enableSharding('yelp_data');

// Create zone tags
print('Creating 5 region zones...');
sh.addShardTag('rs-shard-a', 'PACIFIC');
sh.addShardTag('rs-shard-b', 'MOUNTAIN');
sh.addShardTag('rs-shard-c', 'CENTRAL');
sh.addShardTag('rs-shard-d', 'EASTERN');
sh.addShardTag('rs-shard-e', 'OTHER');

// Shard businesses collection
print('Sharding businesses collection...');
sh.shardCollection('yelp_data.businesses', { state: 1 });

// PACIFIC states
sh.addTagRange('yelp_data.businesses', { state: 'CA' }, { state: 'CB' }, 'PACIFIC');
sh.addTagRange('yelp_data.businesses', { state: 'NV' }, { state: 'NW' }, 'PACIFIC');
sh.addTagRange('yelp_data.businesses', { state: 'OR' }, { state: 'OS' }, 'PACIFIC');
sh.addTagRange('yelp_data.businesses', { state: 'WA' }, { state: 'WB' }, 'PACIFIC');

// MOUNTAIN states
sh.addTagRange('yelp_data.businesses', { state: 'AZ' }, { state: 'BA' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.businesses', { state: 'CO' }, { state: 'CP' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.businesses', { state: 'ID' }, { state: 'IE' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.businesses', { state: 'MT' }, { state: 'MU' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.businesses', { state: 'NM' }, { state: 'NN' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.businesses', { state: 'UT' }, { state: 'UU' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.businesses', { state: 'WY' }, { state: 'WZ' }, 'MOUNTAIN');

// CENTRAL states
sh.addTagRange('yelp_data.businesses', { state: 'IL' }, { state: 'IM' }, 'CENTRAL');
sh.addTagRange('yelp_data.businesses', { state: 'IN' }, { state: 'IO' }, 'CENTRAL');
sh.addTagRange('yelp_data.businesses', { state: 'LA' }, { state: 'LB' }, 'CENTRAL');
sh.addTagRange('yelp_data.businesses', { state: 'MO' }, { state: 'MP' }, 'CENTRAL');
sh.addTagRange('yelp_data.businesses', { state: 'TN' }, { state: 'TO' }, 'CENTRAL');
sh.addTagRange('yelp_data.businesses', { state: 'TX' }, { state: 'TY' }, 'CENTRAL');

// EASTERN states
sh.addTagRange('yelp_data.businesses', { state: 'DE' }, { state: 'DF' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'FL' }, { state: 'FM' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'GA' }, { state: 'HB' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'MA' }, { state: 'MB' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'NC' }, { state: 'ND' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'NJ' }, { state: 'NK' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'NY' }, { state: 'NZ' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'OH' }, { state: 'OI' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'PA' }, { state: 'PB' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'SC' }, { state: 'SD' }, 'EASTERN');
sh.addTagRange('yelp_data.businesses', { state: 'VA' }, { state: 'VB' }, 'EASTERN');

// OTHER states
sh.addTagRange('yelp_data.businesses', { state: 'AB' }, { state: 'AC' }, 'OTHER');
sh.addTagRange('yelp_data.businesses', { state: 'ON' }, { state: 'OO' }, 'OTHER');
sh.addTagRange('yelp_data.businesses', { state: 'QC' }, { state: 'QD' }, 'OTHER');
sh.addTagRange('yelp_data.businesses', { state: 'WI' }, { state: 'WJ' }, 'OTHER');
sh.addTagRange('yelp_data.businesses', { state: 'HI' }, { state: 'HJ' }, 'OTHER');

// Shard reviews collection
print('Sharding reviews collection...');
sh.shardCollection('yelp_data.reviews', { state: 1 });

// Apply same tag ranges to reviews
sh.addTagRange('yelp_data.reviews', { state: 'CA' }, { state: 'CB' }, 'PACIFIC');
sh.addTagRange('yelp_data.reviews', { state: 'NV' }, { state: 'NW' }, 'PACIFIC');
sh.addTagRange('yelp_data.reviews', { state: 'OR' }, { state: 'OS' }, 'PACIFIC');
sh.addTagRange('yelp_data.reviews', { state: 'WA' }, { state: 'WB' }, 'PACIFIC');
sh.addTagRange('yelp_data.reviews', { state: 'AZ' }, { state: 'BA' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'CO' }, { state: 'CP' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'ID' }, { state: 'IE' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'MT' }, { state: 'MU' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'NM' }, { state: 'NN' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'UT' }, { state: 'UU' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'WY' }, { state: 'WZ' }, 'MOUNTAIN');
sh.addTagRange('yelp_data.reviews', { state: 'IL' }, { state: 'IM' }, 'CENTRAL');
sh.addTagRange('yelp_data.reviews', { state: 'IN' }, { state: 'IO' }, 'CENTRAL');
sh.addTagRange('yelp_data.reviews', { state: 'LA' }, { state: 'LB' }, 'CENTRAL');
sh.addTagRange('yelp_data.reviews', { state: 'MO' }, { state: 'MP' }, 'CENTRAL');
sh.addTagRange('yelp_data.reviews', { state: 'TN' }, { state: 'TO' }, 'CENTRAL');
sh.addTagRange('yelp_data.reviews', { state: 'TX' }, { state: 'TY' }, 'CENTRAL');
sh.addTagRange('yelp_data.reviews', { state: 'DE' }, { state: 'DF' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'FL' }, { state: 'FM' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'GA' }, { state: 'HB' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'MA' }, { state: 'MB' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'NC' }, { state: 'ND' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'NJ' }, { state: 'NK' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'NY' }, { state: 'NZ' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'OH' }, { state: 'OI' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'PA' }, { state: 'PB' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'SC' }, { state: 'SD' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'VA' }, { state: 'VB' }, 'EASTERN');
sh.addTagRange('yelp_data.reviews', { state: 'AB' }, { state: 'AC' }, 'OTHER');
sh.addTagRange('yelp_data.reviews', { state: 'ON' }, { state: 'OO' }, 'OTHER');
sh.addTagRange('yelp_data.reviews', { state: 'QC' }, { state: 'QD' }, 'OTHER');
sh.addTagRange('yelp_data.reviews', { state: 'WI' }, { state: 'WJ' }, 'OTHER');
sh.addTagRange('yelp_data.reviews', { state: 'HI' }, { state: 'HJ' }, 'OTHER');

print('Cluster configuration complete!');
" --quiet

echo "✓ Sharding configuration complete"
echo ""

echo "Main cluster initialization complete!"

