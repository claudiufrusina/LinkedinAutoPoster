import os
import json
import sqlite3
from datetime import datetime
from typing import Tuple, Optional
from src.interfaces.content_provider import IContentProvider

class SqliteContentProvider(IContentProvider):
    def __init__(self):
        # Account for being in src/infrastructure (2 levels deep to root)
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        self.db_path = os.path.join(self.data_dir, 'posts.db')
        self.images_dir = os.path.join(self.data_dir, 'images')
        self.template_file = os.path.join(self.data_dir, 'Template.txt')
        self._current_link_id = None
        self._current_text_id = None

        # Initialize the database file and tables if they do not exist
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables column access by name
        return conn

    def _initialize_db(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with self._get_connection() as conn:
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
            conn.commit()

    def get_post_content(self) -> Tuple[str, Optional[str], Optional[dict]]:
        self._current_link_id = None
        self._current_text_id = None
        now = datetime.now()

        with self._get_connection() as conn:
            # 1. Fetch unpublished links
            cursor = conn.execute("""
                SELECT * FROM links 
                WHERE published = 0 
                ORDER BY id ASC
            """)
            links = cursor.fetchall()
            
            link_row = None
            for row in links:
                exp_str = row["expiration_date"]
                if exp_str:
                    try:
                        exp_date = datetime.fromisoformat(exp_str)
                        if exp_date < now:
                            print(f"Post {row['id']} has expired (expired on {exp_date}). Skipping.")
                            # Mark as published/expired in db immediately
                            conn.execute("UPDATE links SET published = 1 WHERE id = ?", (row["id"],))
                            conn.commit()
                            continue
                    except ValueError:
                        print(f"Invalid expiration_date format for {row['id']}. Proceeding anyway.")
                
                link_row = row
                break

            if not link_row:
                return "No valid content available", None, None

            post_id = link_row["id"]

            # 2. Match text by ID
            text_row = conn.execute("SELECT * FROM texts WHERE id = ?", (post_id,)).fetchone()
            if not text_row:
                return "No valid content available", None, None

            last_pub = text_row["last_published"]
            if last_pub:
                print(f"Text '{post_id}' was already published on {last_pub}. Skipping.")
                print("To re-publish, set last_published to NULL or empty string in database.")
                return "No valid content available", None, None

            # Retain IDs for when they are marked as published
            self._current_link_id = link_row["id"]
            self._current_text_id = text_row["id"]

            body_text = text_row["body"]
            body_text = body_text.replace("<br>", "\n")

            # Parse hashtags from JSON string
            hashtags_str = ""
            if text_row["hashtags"]:
                try:
                    hashtags_list = json.loads(text_row["hashtags"])
                    hashtags_str = " ".join(hashtags_list)
                except json.JSONDecodeError:
                    hashtags_str = text_row["hashtags"]

            # 3. Format Template
            post_template = "{body}\n\n{link}"  # Default fallback
            if os.path.exists(self.template_file):
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    post_template = f.read()

            company_name = link_row["company_name"]
            company_urn = link_row["company_urn"]
            company_display = company_name if company_name else ""

            final_text = (
                post_template
                .replace("{title}", link_row["title"])
                .replace("{body}", body_text)
                .replace("{link}", link_row["url"])
                .replace("{hashtags}", hashtags_str)
                .replace("@{Company}", company_display)
            )

            # 4. Resolve Image
            image_path = None
            image_name = link_row["image"]
            if image_name:
                base_image_name = os.path.basename(image_name)
                full_image_path = os.path.join(self.images_dir, base_image_name)
                if os.path.exists(full_image_path):
                    image_path = full_image_path

            # 5. Build mention metadata
            metadata = None
            if company_name and company_urn:
                mention_start = final_text.find(company_name)
                if mention_start != -1:
                    metadata = {
                        "mentions": [
                            {
                                "start": mention_start,
                                "length": len(company_name),
                                "company_urn": company_urn
                            }
                        ]
                    }
                    print(f"Mention detected: '{company_name}' at position {mention_start} (URN: {company_urn})")
                else:
                    print(f"Warning: '{company_name}' not found in the post text. No mention will be tagged.")

            return final_text, image_path, metadata

    def mark_as_published(self) -> None:
        if not self._current_link_id or not self._current_text_id:
            return

        now_str = datetime.now().isoformat()
        with self._get_connection() as conn:
            # Mark link as published
            conn.execute("UPDATE links SET published = 1 WHERE id = ?", (self._current_link_id,))
            # Update text with published timestamp
            conn.execute("UPDATE texts SET last_published = ? WHERE id = ?", (now_str, self._current_text_id))
            conn.commit()

        print(f"Successfully marked link {self._current_link_id} and text {self._current_text_id} as published in SQLite DB.")
        self._current_link_id = None
        self._current_text_id = None
