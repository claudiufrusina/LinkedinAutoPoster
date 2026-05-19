import os
import json
import sqlite3

# Define relative paths in the root directory
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, 'data')
db_path = os.path.join(data_dir, 'posts.db')
links_json_path = os.path.join(data_dir, 'links.json')
texts_json_path = os.path.join(data_dir, 'texts.json')

def migrate():
    print("Starting JSON to SQLite Migration...")
    
    # 1. Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # 2. Connect and initialize DB schemas if not initialized
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS texts (
            id TEXT PRIMARY KEY,
            body TEXT NOT NULL,
            hashtags TEXT,
            last_published TEXT
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            image TEXT,
            expiration_date TEXT,
            company_name TEXT,
            company_urn TEXT,
            published INTEGER DEFAULT 0
        );
    """)
    
    # 3. Migrate links.json
    if os.path.exists(links_json_path):
        with open(links_json_path, 'r', encoding='utf-8') as f:
            try:
                links_data = json.load(f)
                count = 0
                for item in links_data:
                    # Skip the default placeholder item if they don't want it, or migrate everything.
                    # We will migrate everything so they have their database filled.
                    conn.execute("""
                        INSERT OR REPLACE INTO links 
                        (id, url, title, image, expiration_date, company_name, company_urn, published) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item.get("id"),
                        item.get("url"),
                        item.get("title"),
                        item.get("image"),
                        item.get("expiration_date"),
                        item.get("company_name"),
                        item.get("company_urn"),
                        1 if item.get("published", False) else 0
                    ))
                    count += 1
                print(f"Successfully migrated {count} records from links.json into SQLite.")
            except json.JSONDecodeError:
                print("Error: links.json is not valid JSON or is empty.")
    else:
        print(f"links.json not found at {links_json_path}. Skipping links migration.")

    # 4. Migrate texts.json
    if os.path.exists(texts_json_path):
        with open(texts_json_path, 'r', encoding='utf-8') as f:
            try:
                texts_data = json.load(f)
                count = 0
                for item in texts_data:
                    # Convert list of hashtags to JSON string
                    hashtags_str = json.dumps(item.get("hashtags", []))
                    conn.execute("""
                        INSERT OR REPLACE INTO texts 
                        (id, body, hashtags, last_published) 
                        VALUES (?, ?, ?, ?)
                    """, (
                        item.get("id"),
                        item.get("body"),
                        hashtags_str,
                        item.get("last_published")
                    ))
                    count += 1
                print(f"Successfully migrated {count} records from texts.json into SQLite.")
            except json.JSONDecodeError:
                print("Error: texts.json is not valid JSON or is empty.")
    else:
        print(f"texts.json not found at {texts_json_path}. Skipping texts migration.")

    conn.commit()
    conn.close()
    print("\nMigration finished successfully!")
    print(f"SQLite Database generated at: {db_path}")
    print("You can now safely archive/delete links.json and texts.json when ready.")

if __name__ == "__main__":
    migrate()
