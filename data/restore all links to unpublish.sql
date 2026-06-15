-- SQLite restore all links to unpublished and set expiration date to the end of the current month

UPDATE links
SET 
    expiration_date = datetime('now', 'start of month', '+1 month', '-1 second'),
    published = 0;

UPDATE texts
SET last_published = NULL
WHERE last_published IS NOT NULL;