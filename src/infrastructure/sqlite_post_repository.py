import os
import json
import sqlite3
from typing import Optional, List
from src.interfaces.post_repository import IPostRepository


class SqlitePostRepository(IPostRepository):
    """
    Concrete implementation of IPostRepository using SQLite.
    
    Shares the same database (data/posts.db) and table schemas as 
    SqliteContentProvider, but provides write/CRUD operations for the web GUI.
    """

    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = db_path
        else:
            # Default: resolve relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.db_path = os.path.join(base_dir, 'data', 'posts.db')
        
        self._ensure_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        """Ensure tables exist (idempotent, same schema as SqliteContentProvider)."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
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

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convert a sqlite3.Row to a plain dict."""
        return dict(row)

    def _merge_post(self, link_row: sqlite3.Row, text_row: Optional[sqlite3.Row]) -> dict:
        """Merge a link row and text row into a single post dict."""
        post = self._row_to_dict(link_row)
        if text_row:
            text_data = self._row_to_dict(text_row)
            post["body"] = text_data.get("body", "")
            post["hashtags"] = text_data.get("hashtags", "")
            post["last_published"] = text_data.get("last_published", "")
        else:
            post["body"] = ""
            post["hashtags"] = ""
            post["last_published"] = ""
        return post

    def list_posts(self, status_filter: str = "all") -> List[dict]:
        """Retrieve all posts with optional filtering by publication status."""
        with self._get_connection() as conn:
            if status_filter == "pending":
                cursor = conn.execute(
                    "SELECT * FROM links WHERE published = 0 ORDER BY id ASC"
                )
            elif status_filter == "published":
                cursor = conn.execute(
                    "SELECT * FROM links WHERE published = 1 ORDER BY id ASC"
                )
            else:
                cursor = conn.execute("SELECT * FROM links ORDER BY id ASC")

            link_rows = cursor.fetchall()
            posts = []
            for link_row in link_rows:
                text_row = conn.execute(
                    "SELECT * FROM texts WHERE id = ?", (link_row["id"],)
                ).fetchone()
                posts.append(self._merge_post(link_row, text_row))

            return posts

    def get_post(self, post_id: str) -> Optional[dict]:
        """Retrieve a single post by ID, merging link and text data."""
        with self._get_connection() as conn:
            link_row = conn.execute(
                "SELECT * FROM links WHERE id = ?", (post_id,)
            ).fetchone()

            if not link_row:
                return None

            text_row = conn.execute(
                "SELECT * FROM texts WHERE id = ?", (post_id,)
            ).fetchone()

            return self._merge_post(link_row, text_row)

    def create_post(self, data: dict) -> bool:
        """
        Create a new post, inserting into both links and texts tables.
        
        Expects data dict with keys:
            id, title, url, body, hashtags (space-separated string),
            image (filename), expiration_date, company_name, company_urn
        """
        post_id = data.get("id", "").strip()
        if not post_id:
            return False

        # Convert space-separated hashtags to JSON array
        hashtags_raw = data.get("hashtags", "").strip()
        if hashtags_raw:
            tags = [t.strip() for t in hashtags_raw.split() if t.strip()]
            hashtags_json = json.dumps(tags)
        else:
            hashtags_json = "[]"

        try:
            with self._get_connection() as conn:
                # Check if ID already exists
                existing = conn.execute(
                    "SELECT id FROM links WHERE id = ?", (post_id,)
                ).fetchone()
                if existing:
                    return False

                conn.execute("""
                    INSERT INTO links (id, url, title, image, expiration_date, 
                                       company_name, company_urn, published)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    post_id,
                    data.get("url", "").strip(),
                    data.get("title", "").strip(),
                    data.get("image", "").strip() or None,
                    data.get("expiration_date", "").strip() or None,
                    data.get("company_name", "").strip() or None,
                    data.get("company_urn", "").strip() or None,
                ))

                conn.execute("""
                    INSERT INTO texts (id, body, hashtags, last_published)
                    VALUES (?, ?, ?, NULL)
                """, (
                    post_id,
                    data.get("body", "").strip(),
                    hashtags_json,
                ))

                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error creating post: {e}")
            return False

    def update_post(self, post_id: str, data: dict) -> bool:
        """Update an existing post in both links and texts tables."""
        # Convert space-separated hashtags to JSON array
        hashtags_raw = data.get("hashtags", "").strip()
        if hashtags_raw:
            tags = [t.strip() for t in hashtags_raw.split() if t.strip()]
            hashtags_json = json.dumps(tags)
        else:
            hashtags_json = "[]"

        try:
            with self._get_connection() as conn:
                # Check post exists
                existing = conn.execute(
                    "SELECT id FROM links WHERE id = ?", (post_id,)
                ).fetchone()
                if not existing:
                    return False

                conn.execute("""
                    UPDATE links 
                    SET url = ?, title = ?, image = ?, expiration_date = ?,
                        company_name = ?, company_urn = ?
                    WHERE id = ?
                """, (
                    data.get("url", "").strip(),
                    data.get("title", "").strip(),
                    data.get("image", "").strip() or None,
                    data.get("expiration_date", "").strip() or None,
                    data.get("company_name", "").strip() or None,
                    data.get("company_urn", "").strip() or None,
                    post_id,
                ))

                # Upsert texts row (in case it doesn't exist yet)
                conn.execute("""
                    INSERT INTO texts (id, body, hashtags, last_published)
                    VALUES (?, ?, ?, NULL)
                    ON CONFLICT(id) DO UPDATE SET
                        body = excluded.body,
                        hashtags = excluded.hashtags
                """, (
                    post_id,
                    data.get("body", "").strip(),
                    hashtags_json,
                ))

                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error updating post: {e}")
            return False

    def delete_post(self, post_id: str) -> bool:
        """Delete a post from both links and texts tables."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM links WHERE id = ?", (post_id,))
                conn.execute("DELETE FROM texts WHERE id = ?", (post_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error deleting post: {e}")
            return False

    def reset_post(self, post_id: str) -> bool:
        """Reset a published post back to pending status."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "UPDATE links SET published = 0 WHERE id = ?", (post_id,)
                )
                conn.execute(
                    "UPDATE texts SET last_published = NULL WHERE id = ?", (post_id,)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error resetting post: {e}")
            return False
