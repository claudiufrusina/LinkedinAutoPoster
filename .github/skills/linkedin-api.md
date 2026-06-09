# Skill: LinkedIn API Integration

Use this skill when working with LinkedIn API calls, authentication, or publishing logic.

## Authentication
LinkedIn uses OAuth 2.0. The access token is read from `LINKEDIN_ACCESS_TOKEN` env var.
- Tokens expire — handle `401 Unauthorized` by surfacing a clear error message
- Never log the raw token value

## Post Publishing — Three-Step Image Handshake
When a post includes an image, always follow this exact sequence:

### Step 1: Register the Upload
```python
POST https://api.linkedin.com/v2/assets?action=registerUpload
{
  "registerUploadRequest": {
    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
    "owner": "urn:li:person:{PERSON_ID}",
    "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
  }
}
# Response: uploadUrl + asset URN
```

### Step 2: Upload the Binary
```python
PUT {uploadUrl}
Content-Type: application/octet-stream
Body: <raw image bytes>
```

### Step 3: Attach Asset to Post Payload
```python
"content": {
  "media": {
    "status": "READY",
    "media": "{asset_urn}"
  }
}
```

## Text-Only Post Payload
```python
{
  "author": "urn:li:person:{PERSON_ID}",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {"text": "{post_content}"},
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
}
```

## Company @Mentions
Replace `@{Company}` placeholders with URN tags before publishing:
```
{mentionedMember, id=urn:li:organization:12345}
```
The URN mapping lives in the database / config — do not hardcode it.

## Dry-Run Mode
When `DRY_RUN=true`, skip all `requests.post/put` calls and log the payload instead:
```python
if os.getenv("DRY_RUN", "false").lower() == "true":
    logger.info("[DRY RUN] Would publish: %s", payload)
    return
```

## Rate Limits
- LinkedIn API allows ~100 posts/day per token
- Add exponential back-off on `429 Too Many Requests`
