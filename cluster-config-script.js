// -----------------------------------------------------------------
// SCRIPT TO CONFIGURE THE ENTIRE 5-SHARD CLUSTER
// -----------------------------------------------------------------
print("Starting cluster configuration...");

// --- Step 1: Add the 5 Shard Replica Sets to the Cluster ---
print("Step 1/6: Adding the 5 shard replica sets...");
sh.addShard("rs-shard-a/mongo-shard-a-1:27017,mongo-shard-a-2:27017,mongo-shard-a-3:27017")
sh.addShard("rs-shard-b/mongo-shard-b-1:27017,mongo-shard-b-2:27017,mongo-shard-b-3:27017")
sh.addShard("rs-shard-c/mongo-shard-c-1:27017,mongo-shard-c-2:27017,mongo-shard-c-3:27017")
sh.addShard("rs-shard-d/mongo-shard-d-1:27017,mongo-shard-d-2:27017,mongo-shard-d-3:27017")
sh.addShard("rs-shard-e/mongo-shard-e-1:27017,mongo-shard-e-2:27017,mongo-shard-e-3:27017")

// --- Step 2: Enable Sharding on the 'yelp_data' Database ---
print("Step 2/6: Enabling sharding for 'yelp_data' database...");
sh.enableSharding("yelp_data")

// --- Step 3: Create the 5 Region Zones (Tags) ---
print("Step 3/6: Creating 5 region zones (PACIFIC, MOUNTAIN, etc.)...");
sh.addShardTag("rs-shard-a", "PACIFIC")
sh.addShardTag("rs-shard-b", "MOUNTAIN")
sh.addShardTag("rs-shard-c", "CENTRAL")
sh.addShardTag("rs-shard-d", "EASTERN")
sh.addShardTag("rs-shard-e", "OTHER")

// --- Step 4: Shard the 'businesses' Collection & Apply Ranges ---
print("Step 4/6: Sharding 'businesses' collection and applying region rules...");
sh.shardCollection("yelp_data.businesses", { "state": 1 } )
// PACIFIC
sh.addTagRange("yelp_data.businesses", { "state": "CA" }, { "state": "CB" }, "PACIFIC")
sh.addTagRange("yelp_data.businesses", { "state": "NV" }, { "state": "NW" }, "PACIFIC")
sh.addTagRange("yelp_data.businesses", { "state": "OR" }, { "state": "OS" }, "PACIFIC")
sh.addTagRange("yelp_data.businesses", { "state": "WA" }, { "state": "WB" }, "PACIFIC")
// MOUNTAIN
sh.addTagRange("yelp_data.businesses", { "state": "AZ" }, { "state": "BA" }, "MOUNTAIN")
sh.addTagRange("yelp_data.businesses", { "state": "CO" }, { "state": "CP" }, "MOUNTAIN")
sh.addTagRange("yelp_data.businesses", { "state": "ID" }, { "state": "IE" }, "MOUNTAIN")
sh.addTagRange("yelp_data.businesses", { "state": "MT" }, { "state": "MU" }, "MOUNTAIN")
sh.addTagRange("yelp_data.businesses", { "state": "NM" }, { "state": "NN" }, "MOUNTAIN")
sh.addTagRange("yelp_data.businesses", { "state": "UT" }, { "state": "UU" }, "MOUNTAIN")
sh.addTagRange("yelp_data.businesses", { "state": "WY" }, { "state": "WZ" }, "MOUNTAIN")
// CENTRAL
sh.addTagRange("yelp_data.businesses", { "state": "IL" }, { "state": "IM" }, "CENTRAL")
sh.addTagRange("yelp_data.businesses", { "state": "IN" }, { "state": "IO" }, "CENTRAL")
sh.addTagRange("yelp_data.businesses", { "state": "LA" }, { "state": "LB" }, "CENTRAL")
sh.addTagRange("yelp_data.businesses", { "state": "MO" }, { "state": "MP" }, "CENTRAL")
sh.addTagRange("yelp_data.businesses", { "state": "TN" }, { "state": "TO" }, "CENTRAL")
sh.addTagRange("yelp_data.businesses", { "state": "TX" }, { "state": "TY" }, "CENTRAL")
// EASTERN
sh.addTagRange("yelp_data.businesses", { "state": "DE" }, { "state": "DF" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "FL" }, { "state":"FM" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "GA" }, { "state": "HB" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "MA" }, { "state": "MB" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "NC" }, { "state":"ND" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "NJ" }, { "state": "NK" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "NY" }, { "state": "NZ" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "OH" }, { "state": "OI" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "PA" }, { "state": "PB" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "SC" }, { "state": "SD" }, "EASTERN")
sh.addTagRange("yelp_data.businesses", { "state": "VA" }, { "state": "VB" }, "EASTERN")
// OTHER
sh.addTagRange("yelp_data.businesses", { "state": "AB" }, { "state": "AC" }, "OTHER")
sh.addTagRange("yelp_data.businesses", { "state": "ON" }, { "state": "OO" }, "OTHER")
sh.addTagRange("yelp_data.businesses", { "state": "QC" }, { "state": "QD" }, "OTHER")
sh.addTagRange("yelp_data.businesses", { "state": "WI" }, { "state": "WJ" }, "OTHER")
sh.addTagRange("yelp_data.businesses", { "state": "HI" }, { "state": "HJ" }, "OTHER")

// --- Step 5: Shard the 'reviews' Collection & Apply Ranges ---
print("Step 5/6: Sharding 'reviews' collection and applying region rules...");
sh.shardCollection("yelp_data.reviews", { "state": 1 } )
// PACIFIC
sh.addTagRange("yelp_data.reviews", { "state": "CA" }, { "state": "CB" }, "PACIFIC")
sh.addTagRange("yelp_data.reviews", { "state": "NV" }, { "state": "NW" }, "PACIFIC")
sh.addTagRange("yelp_data.reviews", { "state": "OR" }, { "state": "OS" }, "PACIFIC")
sh.addTagRange("yelp_data.reviews", { "state": "WA" }, { "state": "WB" }, "PACIFIC")
// MOUNTAIN
sh.addTagRange("yelp_data.reviews", { "state": "AZ" }, { "state": "BA" }, "MOUNTAIN")
sh.addTagRange("yelp_data.reviews", { "state": "CO" }, { "state": "CP" }, "MOUNTAIN")
sh.addTagRange("yelp_data.reviews", { "state": "ID" }, { "state": "IE" }, "MOUNTAIN")
sh.addTagRange("yelp_data.reviews", { "state": "MT" }, { "state": "MU" }, "MOUNTAIN")
sh.addTagRange("yelp_data.reviews", { "state": "NM" }, { "state": "NN" }, "MOUNTAIN")
sh.addTagRange("yelp_data.reviews", { "state": "UT" }, { "state": "UU" }, "MOUNTAIN")
sh.addTagRange("yelp_data.reviews", { "state": "WY" }, { "state": "WZ" }, "MOUNTAIN")
// CENTRAL
sh.addTagRange("yelp_data.reviews", { "state": "IL" }, { "state": "IM" }, "CENTRAL")
sh.addTagRange("yelp_data.reviews", { "state": "IN" }, { "state": "IO" }, "CENTRAL")
sh.addTagRange("yelp_data.reviews", { "state": "LA" }, { "state": "LB" }, "CENTRAL")
sh.addTagRange("yelp_data.reviews", { "state": "MO" }, { "state": "MP" }, "CENTRAL")
sh.addTagRange("yelp_data.reviews", { "state": "TN" }, { "state": "TO" }, "CENTRAL")
sh.addTagRange("yelp_data.reviews", { "state": "TX" }, { "state": "TY" }, "CENTRAL")
// EASTERN
sh.addTagRange("yelp_data.reviews", { "state": "DE" }, { "state": "DF" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "FL" }, { "state": "FM" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "GA" }, { "state": "HB" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "MA" }, { "state": "MB" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "NC" }, { "state": "ND" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "NJ" }, { "state": "NK" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "NY" }, { "state": "NZ" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "OH" }, { "state": "OI" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "PA" }, { "state": "PB" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "SC" }, { "state": "SD" }, "EASTERN")
sh.addTagRange("yelp_data.reviews", { "state": "VA" }, { "state": "VB" }, "EASTERN")
// OTHER
sh.addTagRange("yelp_data.reviews", { "state": "AB" }, { "state": "AC" }, "OTHER")
sh.addTagRange("yelp_data.reviews", { "state": "ON" }, { "state": "OO" }, "OTHER")
sh.addTagRange("yelp_data.reviews", { "state": "QC" }, { "state": "QD" }, "OTHER")
sh.addTagRange("yelp_data.reviews", { "state": "WI" }, { "state": "WJ" }, "OTHER")
sh.addTagRange("yelp_data.reviews", { "state": "HI" }, { "state": "HJ" }, "OTHER")

// --- Step 6: Create Indexes (Faster to do before inserting) ---
print("Step 6/6: Creating indexes on both collections...");
var yelpDb = db.getSiblingDB("yelp_data");
yelpDb.businesses.createIndex( { "location": "2dsphere" } );
yelpDb.businesses.createIndex( { "state": 1 } ); // Shard key is auto-indexed, but good practice
yelpDb.reviews.createIndex( { "location": "2dsphere" } );
yelpDb.reviews.createIndex( { "business_id": 1 } );
yelpDb.reviews.createIndex( { "user_id": 1 } );
yelpDb.reviews.createIndex( { "state": 1 } );

print("✅✅✅ CLUSTER CONFIGURATION COMPLETE! ✅✅✅");
print("Your cluster is now ready for data insertion.");
exit

