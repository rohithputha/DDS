import json
import orjson
# Configuation
INPUT_FILE = 'data/user.subset.json'
OUTPUT_FILE = 'data/user.subset.with_passwords.json'
PASSWORD = 'yelp2024'  
print("Starting password addition process...")
print(f"Reading from: {INPUT_FILE}")
print(f"Writing to: {OUTPUT_FILE}")
line_count = 0
with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
     open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    
    for line in infile:
        # Parse the JSON line
        user = orjson.loads(line.strip())
        
        # Add password field
        user['password'] = PASSWORD
        
        # Write back as JSON line
        outfile.write(orjson.dumps(user).decode('utf-8'))
        outfile.write('\n')
        
        line_count += 1
        if line_count % 10000 == 0:
            print(f"Processed {line_count} users...")
print(f"✓ Complete! Processed {line_count} total users.")
print(f"✓ Output file: {OUTPUT_FILE}")