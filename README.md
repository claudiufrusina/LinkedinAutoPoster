# 🚀 LinkedIn Auto Poster

Welcome to the **LinkedIn Auto Poster**! This project is an automated, scheduled Python application designed to dynamically compose and publish posts (text + images + @mentions) to your LinkedIn profile. It follows a clean, SOLID architecture for maximum scalability.

It includes a **Web GUI** for creating and managing posts through a premium dark-themed dashboard, and a **scheduler** that automatically publishes them to LinkedIn at configured times.

---

## 📁 Project Structure

```
LinkedinAutoPosts/
├── main.py                  # Scheduler entry point (auto-publishes posts)
├── web.py                   # Web GUI entry point (manage posts via browser)
├── migrate_to_sqlite.py     # One-time JSON → SQLite migration script
├── run_poster.bat           # One-click Windows launcher
├── run_poster.sh            # Linux/Ubuntu bash launcher
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose orchestration
├── .dockerignore            # Excludes build cache & local files
├── .env                     # Environment variables (secrets)
├── data/
│   ├── posts.db             # SQLite database (links + texts tables)
│   ├── Template.txt         # Post layout template
│   ├── images/              # Image assets for posts
│   ├── links.json           # (Legacy) JSON post queue
│   └── texts.json           # (Legacy) JSON content database
├── templates/               # Jinja2 HTML templates for the Web GUI
│   ├── base.html            # Layout shell (nav, flash messages, JS)
│   ├── dashboard.html       # Post listing with stats & filters
│   ├── post_form.html       # Create/edit form with image upload
│   └── preview.html         # LinkedIn-style post preview
├── static/
│   └── style.css            # Premium dark-themed stylesheet
└── src/
    ├── config.py             # Reads .env settings
    ├── core/
    │   └── post_service.py   # Orchestrates the full pipeline
    ├── infrastructure/
    │   ├── auth.py                    # OAuth & token helper
    │   ├── file_content_provider.py   # (Legacy) JSON-based content loader
    │   ├── sqlite_content_provider.py # SQLite-based content loader (scheduler)
    │   ├── sqlite_post_repository.py  # SQLite-based CRUD (Web GUI)
    │   └── linkedin_client.py         # LinkedIn API integration
    └── interfaces/
        ├── content_provider.py  # IContentProvider (read-only, publishing)
        ├── post_repository.py   # IPostRepository (CRUD operations)
        └── social_client.py     # ISocialClient abstraction
```

---

## 🖥️ Web GUI — Post Manager

The project includes a **Flask-based web dashboard** for managing your posts visually — no need to edit database files by hand.

### Starting the Web GUI
```bash
python web.py
```
Then open **http://localhost:5001** in your browser.

> 💡 **Custom port:** Set `WEB_PORT=8080` in your `.env` file or as an environment variable.

### Features
| Feature | Description |
|---|---|
| 📊 **Dashboard** | View all posts with status badges (Pending / Published / Expired), stats bar, and filter buttons |
| ➕ **Create Post** | Fill in title, URL, body, hashtags, company mention, expiration date, and upload an image |
| ✏️ **Edit Post** | Modify any field of an existing post, including replacing the image |
| 👁️ **Preview** | See exactly how your post will look on LinkedIn, rendered through your `Template.txt` |
| 🔄 **Reset** | Re-queue a published post back to pending status |
| 🗑️ **Delete** | Remove a post and its associated image |
| 🆔 **Auto-ID** | Leave the Post ID field empty and a unique ID will be auto-generated |

> 📝 The Web GUI runs independently from the scheduler (`main.py`). Both share the same `data/posts.db` database and can run simultaneously.

---

## 💾 Data Storage — SQLite Database

All post data is stored in a local **SQLite database** at `data/posts.db`. No external database server is needed — Python's built-in `sqlite3` module handles everything.

The database contains two tables:

### `links` table (Post metadata & queue)
| Column | Type | Description |
|---|---|---|
| `id` | TEXT (PK) | Unique post identifier |
| `url` | TEXT | URL to share |
| `title` | TEXT | Post headline |
| `image` | TEXT | Image filename in `data/images/` |
| `expiration_date` | TEXT | ISO datetime (auto-skipped if past) |
| `company_name` | TEXT | Company display name for @mention |
| `company_urn` | TEXT | LinkedIn organization URN |
| `published` | INTEGER | `0` = pending, `1` = published |

### `texts` table (Post content)
| Column | Type | Description |
|---|---|---|
| `id` | TEXT (PK) | Matches the link ID |
| `body` | TEXT | Post body text |
| `hashtags` | TEXT | JSON array, e.g. `["#job", "#hiring"]` |
| `last_published` | TEXT | ISO timestamp of last publish |

> 💡 **Migrating from JSON files:** If you have existing data in `links.json` and `texts.json`, run `python migrate_to_sqlite.py` to import them into the database.

---

## ⚙️ How the Scheduler Pipeline Works

The scheduler (`main.py`) uses an intelligent queuing system to build and publish your posts automatically. Here is what happens when a scheduled post triggers:

### 1. 📋 The Queue (`links` table)
The scheduler scans the `links` table looking for the next valid entry:
- ✅ **Published Check:** It skips any entry where `published = 1`.
- ⏳ **Expiration Check:** It checks the `expiration_date`. If that date is in the past, it automatically marks the entry as published and moves on.
- 🎯 **Extraction:** Once it finds a valid link, it extracts the `id`, `url`, `title`, `image` filename, and optional `company_name` / `company_urn` for @mentions.
- 🔒 **Safe Marking:** After a successful publish, it sets `published = 1`. Your data is **never destructively modified** — only the flag changes.

### 2. 🗄️ The Content (`texts` table)
Next, the scheduler looks up the matching text entry:
- 🔍 It finds the row where the `id` matches the link's ID.
- 🛡️ **Duplicate Prevention:** It checks `last_published`. If it contains a timestamp, the post is **skipped automatically** — no duplicates.
- ✍️ It extracts the `body` text and `hashtags` array.
- 📝 Any `<br>` tags in the body are converted to real newlines for LinkedIn formatting.

> 💡 **Re-publishing a post:** Use the Web GUI's **Reset** button, or manually set `last_published = NULL` in the `texts` table and `published = 0` in the `links` table.

### 3. 🧩 The Assembler (`data/Template.txt`)
Now the script has a raw text body, a URL, a title, and hashtags — but it needs to format them.
- 📄 It opens your `Template.txt` file and looks for the special placeholder tags.
- 💉 It dynamically injects each piece of content into the matching placeholders.
- ✨ Any emojis, spacing, or fixed tags in your template are automatically applied to the final message!

**Available placeholders:**

| Placeholder | Source | Description |
|---|---|---|
| `{title}` | `links.json` → `title` | Post headline |
| `{body}` | `texts.json` → `body` | Main post text |
| `{link}` | `links.json` → `url` | URL to share |
| `{hashtags}` | `texts.json` → `hashtags[]` | Space-separated hashtags |
| `@{Company}` | `links.json` → `company_name` | Tagged company name (becomes a clickable @mention) |

**Example template:**
```
🚀{title}

{body}

@{Company}
👉 Find out more here: {link}

#AutoGeneratedByMyLinkedinBot
{hashtags}
```

### 4. 🏷️ Company @Mentions
If a link entry includes both `company_name` and `company_urn`, the script will:
1. 🔎 Locate the company name inside the final assembled text.
2. 📐 Calculate its exact character position and length.
3. 🤝 Attach LinkedIn's `CompanyAttributedEntity` metadata to the API payload.
4. ✨ The company name becomes a **clickable @mention** in the published post!

> 💡 **Tip:** Leave `company_name` and `company_urn` empty if you don't need a mention for that post.

### 5. 🖼️ The Image Upload Process
The script looks at the `"image"` attribute from the link entry (e.g., `"article_banner.png"`).
1. 📁 It searches inside your `data/images/` folder for a file with that exact name.
2. 🤝 If found, it sends a secure "handshake" request to the LinkedIn API asking for permission to upload an image.
3. 🔗 LinkedIn responds with a temporary, secure upload URL.
4. ☁️ The script uploads the actual binary file to that URL.
5. 🔑 LinkedIn processes the image and gives the script an `Asset URN` (a unique ID for that specific uploaded image).

> 💡 **Note:** If you didn't specify an image, or if the image file was missing from the folder, the script safely falls back to creating a text-only post.

### 6. 🚀 Publishing to LinkedIn
Finally, the script packages the formatted text (from step 3), the mention metadata (from step 4), and the `Asset URN` (from step 5) into one final JSON payload and sends it to the LinkedIn API.
🎉 The post goes live instantly with the text, the URL, the @mention, and the attached image!

After a successful publish:
- ✅ The link entry in `links.json` is marked with `"published": true`
- 📅 The text entry in `texts.json` gets stamped with the current date/time in `"last_published"`

---

## 🔶 Dry Run Mode

Test your entire pipeline **without actually publishing** to LinkedIn. In dry-run mode the script assembles the full post, prints it to the console, and then exits — nothing is sent to the API and no data is modified.

**Enable it in one of two ways:**

| Method | How |
|---|---|
| `.env` variable | Add `DRY_RUN=true` to your `.env` file |
| Command-line flag | Run with `python main.py --dry-run` |

---

## 🛠️ Setup & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure `.env`
Create a `.env` file in the project root with the following variables:

```env
# LinkedIn App Credentials
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_URN=urn:li:person:your_person_id

# Posting Schedule (comma-separated 24h times)
POSTING_TIMES=10:00,14:30

# Optional settings
MAX_POSTS_PER_DAY=2
DRY_RUN=false
```

### 3. Add Your Content

You can add content in **two ways**:

#### Option A: Web GUI (Recommended)
```bash
python web.py
```
Open **http://localhost:5001**, click **"Create New Post"**, fill in the form, upload an image, and submit.

#### Option B: Manual Database Entry
If you prefer, use any SQLite client (e.g., DB Browser for SQLite) to insert rows directly into the `links` and `texts` tables in `data/posts.db`.

> 💡 **Migrating legacy JSON data:** If you have existing `links.json` / `texts.json` files, run `python migrate_to_sqlite.py` once to import them.

### 4. Launch!

#### 🖥️ Web GUI (manage posts)
```bash
python web.py
```

#### 💻 Scheduler (auto-publish)
* **Windows** (double-click or run):
  ```bash
  run_poster.bat
  ```
* **Ubuntu / Linux**:
  ```bash
  chmod +x run_poster.sh
  ./run_poster.sh
  ```
* **Manual execution**:
  ```bash
  python3 main.py
  ```
* **Test without publishing (Dry Run)**:
  ```bash
  python3 main.py --dry-run
  ```

---

## 🐳 Docker Deployment

The application includes full support for running inside Docker. Docker encapsulates all libraries, timezone differences, and network connectivity dependencies.

### 1. Requirements
* Docker installed on Windows (Docker Desktop) or Ubuntu.
* Docker Compose installed.

### 2. Standard Launch (Docker Compose)
Docker Compose handles volume mounts so that modifications to post queues (`links.json`, `texts.json`) write back directly to the host machine.

* **Build and run in the background:**
  ```bash
  docker-compose up -d --build
  ```
* **Follow live logs:**
  ```bash
  docker-compose logs -f
  ```
* **Stop the container:**
  ```bash
  docker-compose down
  ```

### 3. Custom Timezone
The scheduler respects your local timezone by reading the `TZ` environment variable. You can customize this by editing the `environment` section of `docker-compose.yml`:
```yaml
environment:
  - TZ=Europe/Rome  # Change to your local Olson timezone ID
```

---

## 📊 Content Lifecycle at a Glance

```
                    ┌──────────────────┐
                    │   Web GUI 🖥️     │
                    │  (create/edit/   │
                    │   upload/reset)  │
                    └────────┬─────────┘
                             │
                             ▼
┌──────────────────────────────────────────┐
│          SQLite Database (posts.db)      │
│  ┌─────────────┐    ┌──────────────┐     │
│  │ links table │    │ texts table  │     │
│  │ published=0 │    │last_published│     │
│  └──────┬──────┘    └──────┬───────┘     │
└─────────┼──────────────────┼─────────────┘
          │                  │
          ▼                  ▼
   ┌──────────────┐   ┌──────────────┐   ┌────────────┐
   │  Scheduler   │──▸│ Template.txt │──▸│  LinkedIn  │
   │  (main.py)   │   │  {body}      │   │   API 🚀   │
   └──────────────┘   │  {link} ...  │   └─────┬──────┘
                      └──────────────┘         │
                                               ▼
                                    published = 1
                                    last_published = now()
```

> 🔁 **Want to re-publish?** Click the **Reset** button in the Web GUI, or set `published = 0` in `links` and `last_published = NULL` in `texts`.
