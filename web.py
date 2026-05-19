import os
import json
import uuid
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_from_directory
)
from werkzeug.utils import secure_filename
from src.infrastructure.sqlite_post_repository import SqlitePostRepository

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "linkedin-post-manager-dev-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
TEMPLATE_FILE = os.path.join(DATA_DIR, "Template.txt")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# ---------------------------------------------------------------------------
# Dependency: Repository
# ---------------------------------------------------------------------------
repo = SqlitePostRepository()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _parse_hashtags_to_list(hashtags_json: str) -> list:
    """Convert a JSON array string like '["#a","#b"]' to a Python list."""
    if not hashtags_json:
        return []
    try:
        tags = json.loads(hashtags_json)
        if isinstance(tags, list):
            return tags
    except json.JSONDecodeError:
        pass
    return []


def _parse_hashtags_for_display(hashtags_json: str) -> str:
    """Convert a JSON array string like '["#a","#b"]' to a space-separated string."""
    return " ".join(_parse_hashtags_to_list(hashtags_json))


def _enrich_post(post: dict) -> dict:
    """Enrich a post dict with parsed hashtags list and display string for templates."""
    raw = post.get("hashtags", "")
    post["hashtags_list"] = _parse_hashtags_to_list(raw)
    post["hashtags_display"] = " ".join(post["hashtags_list"])
    return post


def _render_preview(post: dict) -> str:
    """Render the post through Template.txt, exactly as the scheduler would."""
    template_text = "{body}\n\n{link}"
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            template_text = f.read()

    body = (post.get("body") or "").replace("<br>", "\n")
    hashtags_str = _parse_hashtags_for_display(post.get("hashtags", ""))
    company_display = post.get("company_name") or ""

    return (
        template_text
        .replace("{title}", post.get("title", ""))
        .replace("{body}", body)
        .replace("{link}", post.get("url", ""))
        .replace("{hashtags}", hashtags_str)
        .replace("@{Company}", company_display)
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    status_filter = request.args.get("status", "all")
    posts = repo.list_posts(status_filter)

    # Enrich posts with parsed hashtags for templates
    for post in posts:
        _enrich_post(post)

    # Compute stats
    all_posts = repo.list_posts("all")
    stats = {
        "total": len(all_posts),
        "pending": sum(1 for p in all_posts if p.get("published") == 0),
        "published": sum(1 for p in all_posts if p.get("published") == 1),
    }

    return render_template(
        "dashboard.html",
        posts=posts,
        stats=stats,
        status_filter=status_filter,
        now=datetime.now().isoformat(),
    )


@app.route("/posts/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        data = {
            "id": request.form.get("id", "").strip(),
            "title": request.form.get("title", "").strip(),
            "url": request.form.get("url", "").strip(),
            "body": request.form.get("body", "").strip(),
            "hashtags": request.form.get("hashtags", "").strip(),
            "company_name": request.form.get("company_name", "").strip(),
            "company_urn": request.form.get("company_urn", "").strip(),
            "expiration_date": request.form.get("expiration_date", "").strip(),
            "image": "",
        }

        # Auto-generate ID if left empty
        if not data["id"]:
            data["id"] = uuid.uuid4().hex[:12]

        # Validate required fields
        if not data["title"] or not data["url"] or not data["body"]:
            flash("Title, URL, and Body are required.", "error")
            return render_template("post_form.html", post=data)

        # Handle image upload
        file = request.files.get("image")
        if file and file.filename and _allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(IMAGES_DIR, exist_ok=True)
            file.save(os.path.join(IMAGES_DIR, filename))
            data["image"] = filename

        success = repo.create_post(data)
        if success:
            flash(f"Post '{data['id']}' created successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash(f"Failed to create post. ID '{data['id']}' may already exist.", "error")
            return render_template("post_form.html", post=data)

    return render_template("post_form.html", post=None)


@app.route("/posts/<post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id: str):
    post = repo.get_post(post_id)
    if not post:
        flash(f"Post '{post_id}' not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        data = {
            "title": request.form.get("title", "").strip(),
            "url": request.form.get("url", "").strip(),
            "body": request.form.get("body", "").strip(),
            "hashtags": request.form.get("hashtags", "").strip(),
            "company_name": request.form.get("company_name", "").strip(),
            "company_urn": request.form.get("company_urn", "").strip(),
            "expiration_date": request.form.get("expiration_date", "").strip(),
            "image": post.get("image") or "",  # Keep existing image by default
        }

        # Handle new image upload
        file = request.files.get("image")
        if file and file.filename and _allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(IMAGES_DIR, exist_ok=True)
            file.save(os.path.join(IMAGES_DIR, filename))
            data["image"] = filename

        success = repo.update_post(post_id, data)
        if success:
            flash(f"Post '{post_id}' updated successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Failed to update post.", "error")

        # Re-merge for display
        post.update(data)
        post["id"] = post_id

    # Prepare hashtags for the form (convert JSON array to space-separated)
    _enrich_post(post)

    return render_template("post_form.html", post=post)


@app.route("/posts/<post_id>/delete", methods=["POST"])
def delete_post(post_id: str):
    post = repo.get_post(post_id)

    # Attempt to remove associated image file
    if post and post.get("image"):
        image_path = os.path.join(IMAGES_DIR, post["image"])
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except OSError:
                pass

    success = repo.delete_post(post_id)
    if success:
        flash(f"Post '{post_id}' deleted.", "success")
    else:
        flash(f"Failed to delete post '{post_id}'.", "error")

    return redirect(url_for("index"))


@app.route("/posts/<post_id>/reset", methods=["POST"])
def reset_post(post_id: str):
    success = repo.reset_post(post_id)
    if success:
        flash(f"Post '{post_id}' has been reset to pending.", "success")
    else:
        flash(f"Failed to reset post '{post_id}'.", "error")

    return redirect(url_for("index"))


@app.route("/posts/<post_id>/preview")
def preview_post(post_id: str):
    post = repo.get_post(post_id)
    if not post:
        flash(f"Post '{post_id}' not found.", "error")
        return redirect(url_for("index"))

    preview_text = _render_preview(post)
    _enrich_post(post)

    return render_template(
        "preview.html",
        post=post,
        preview_text=preview_text,
        now=datetime.now().isoformat(),
    )


@app.route("/images/<filename>")
def serve_image(filename: str):
    """Serve uploaded images from the data/images directory."""
    return send_from_directory(IMAGES_DIR, filename)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("WEB_PORT", 5000))
    print(f"Starting LinkedIn Post Manager on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
