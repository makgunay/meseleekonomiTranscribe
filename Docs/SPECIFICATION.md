# YouTube Channel Video Extractor - Technical Specification

## 1. System Overview

A tool for extracting comprehensive video metadata from YouTube channels using the YouTube Data API v3. The system retrieves all videos from a specified channel and exports the data in both CSV and JSON formats with full metadata including statistics, duration, and tags.

**Primary Use Cases:**
- Channel content analysis and archiving
- Video statistics tracking and reporting
- Content audit and inventory management
- Historical data collection for analytics

---

## 2. Core Functionality

### 2.1 Main Features
1. **Channel Video Extraction**: Retrieve all videos from a YouTube channel by channel ID
2. **Dual Format Export**: Save data in both CSV and JSON formats simultaneously
3. **Full Metadata Capture**: Extract comprehensive video information including statistics, duration, and tags
4. **OAuth Authentication**: Secure authentication with token refresh capability
5. **Duration Analysis**: Optional tool for analyzing video duration patterns over time periods

### 2.2 Key Capabilities
- Handle channels with 1000+ videos through pagination
- Automatic token refresh for long-running sessions
- Graceful handling of missing optional fields
- ISO 8601 duration parsing and analysis

---

## 3. Authentication Flow

### 3.1 OAuth 2.0 Implementation

**Authentication Method**: OAuth 2.0 with offline access for refresh tokens

**Required Scope**:
```
https://www.googleapis.com/auth/youtube.force-ssl
```

**Token Management**:
1. Check for existing `token.json` file containing saved credentials
2. If token exists and is valid, use it for API calls
3. If token is expired but has refresh token, automatically refresh
4. If no valid token exists, initiate browser-based OAuth flow
5. Save new credentials to `token.json` for future use

**Implementation Details**:
```
- Token file: token.json (gitignored)
- Client secrets file: client_secret.json (gitignored)
- OAuth flow: InstalledAppFlow with local server (port 0 = auto-assign)
- Environment variable: OAUTHLIB_INSECURE_TRANSPORT=1 (development only)
```

**Error Scenarios**:
- **HttpError 403**: API quota exceeded or invalid credentials
- **RefreshError**: Token invalid, delete `token.json` and re-authenticate
- **Missing client_secret.json**: Download from Google Cloud Console

---

## 4. API Integration Architecture

### 4.1 Two-Stage Data Fetching Pattern

The YouTube Data API requires a two-stage approach because playlist item endpoints don't include statistics or content details.

**Stage 1: Get Channel Information**
```
Endpoint: channels().list()
Parameters:
  - part: "contentDetails,snippet"
  - id: {channel_id}
Cost: 1 quota unit

Returns:
  - uploads_playlist_id: Special playlist containing all channel uploads
  - channel_name: Display name of the channel
```

**Stage 2: Get All Videos (Paginated)**

**Step 2A: Fetch Video IDs from Playlist**
```
Endpoint: playlistItems().list()
Parameters:
  - part: "snippet"
  - playlistId: {uploads_playlist_id}
  - maxResults: 50 (API maximum)
  - pageToken: {next_page_token} (for pagination)
Cost: 1 quota unit per page

Returns:
  - Array of video IDs
  - nextPageToken for pagination
```

**Step 2B: Batch Fetch Video Details**
```
Endpoint: videos().list()
Parameters:
  - part: "snippet,contentDetails,statistics"
  - id: {comma_separated_video_ids} (batch of up to 50)
Cost: 1 quota unit per batch

Returns:
  - Complete video metadata including statistics and duration
```

### 4.2 Pagination Logic

```
1. Initialize empty video_ids array
2. Request playlist page (50 items max)
3. Collect video IDs from response
4. When video_ids reaches 50 OR no more pages:
   a. Batch fetch full details for collected IDs
   b. Process and store video data
   c. Clear video_ids array
5. Check for nextPageToken
6. If token exists, repeat from step 2
7. If no token, processing complete
```

### 4.3 API Quota Considerations

**Daily Quota**: 10,000 units

**Cost Breakdown**:
- Channel info lookup: 1 unit
- Each playlist page (50 videos): 1 unit
- Each video details batch (50 videos): 1 unit
- Total for 1000 videos: 1 + 20 + 20 = 41 units

**Large Channel Example** (2000 videos):
- Channel info: 1 unit
- Playlist pages: 40 units (2000 ÷ 50)
- Video details: 40 units (2000 ÷ 50)
- Total: 81 units (8.1% of daily quota)

---

## 5. Data Models

### 5.1 Video Information Object

**Structure**:
```json
{
  "video_id": "string",
  "title": "string",
  "description": "string (full text)",
  "link": "string (formatted URL)",
  "publish_date": "string (ISO 8601 with timezone)",
  "view_count": "string or 'N/A'",
  "like_count": "string or 'N/A'",
  "comment_count": "string or 'N/A'",
  "duration": "string (ISO 8601 format)",
  "tags": "array of strings",
  "category_id": "string"
}
```

**Field Details**:

| Field | Type | Required | Format | Notes |
|-------|------|----------|--------|-------|
| video_id | string | Yes | 11 characters | Unique YouTube video identifier |
| title | string | Yes | - | Video title as displayed on YouTube |
| description | string | Yes | - | Full video description (can be empty) |
| link | string | Yes | `https://www.youtube.com/watch?v={video_id}` | Constructed watch URL |
| publish_date | string | Yes | ISO 8601 | Format: `2024-08-12T15:30:00Z` |
| view_count | string | No | Numeric string | Use `.get()`, default 'N/A' if missing |
| like_count | string | No | Numeric string | Use `.get()`, default 'N/A' if missing |
| comment_count | string | No | Numeric string | Use `.get()`, default 'N/A' if missing |
| duration | string | Yes | ISO 8601 | Format: `PT4M33S` (4 min 33 sec) |
| tags | array | No | Array of strings | Use `.get()`, default empty array |
| category_id | string | Yes | Numeric string | YouTube category identifier |

**Optional Field Handling**: Statistics fields (viewCount, likeCount, commentCount) and tags may be unavailable based on video privacy settings. Always use `.get()` method with default values.

### 5.2 Duration Format (ISO 8601)

**Pattern**: `PT[hours]H[minutes]M[seconds]S`

**Examples**:
- `PT4M33S` = 4 minutes, 33 seconds
- `PT1H30M15S` = 1 hour, 30 minutes, 15 seconds
- `PT45S` = 45 seconds
- `PT2H5M` = 2 hours, 5 minutes (0 seconds omitted)

**Parsing Regex**:
```regex
PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?
```

**Conversion to Seconds**:
```
total_seconds = (hours × 3600) + (minutes × 60) + seconds
```

---

## 6. File Output Formats

### 6.1 File Naming Convention

**Pattern**: `{sanitized_channel_name}_{YYYYMMDD}_{video_count}.{extension}`

**Sanitization Rules**:
- Keep only alphanumeric characters, spaces, hyphens, and underscores
- Remove all other special characters
- Trim leading/trailing whitespace

**Examples**:
- `Mesele Ekonomi_20250812_2138.csv`
- `Tech Reviews_20251018_456.json`

### 6.2 CSV Format

**Encoding**: UTF-8 with BOM
**Newline**: Platform default
**Delimiter**: Comma
**Quote Character**: Double quote (for fields containing commas/newlines)

**Field Order** (11 columns):
```
video_id, title, description, link, publish_date, view_count, like_count, comment_count, duration, tags, category_id
```

**Tags Representation**: Comma-separated string within the cell
- Example: `"economics, finance, turkey"`
- If no tags: empty string

**Sample Row**:
```csv
dQw4w9WgXcQ,"Never Gonna Give You Up","Official music video...","https://www.youtube.com/watch?v=dQw4w9WgXcQ","2009-10-25T06:57:33Z","1500000000","25000000","3500000","PT3M33S","music, 80s, rick astley","10"
```

### 6.3 JSON Format

**Structure**:
```json
{
  "channel_name": "Original channel name (not sanitized)",
  "export_date": "YYYYMMDD",
  "video_count": 2138,
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "title": "Never Gonna Give You Up",
      "description": "Official music video...",
      "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "publish_date": "2009-10-25T06:57:33Z",
      "view_count": "1500000000",
      "like_count": "25000000",
      "comment_count": "3500000",
      "duration": "PT3M33S",
      "tags": ["music", "80s", "rick astley"],
      "category_id": "10"
    }
  ]
}
```

**Key Differences from CSV**:
- Tags stored as array, not comma-separated string
- Includes metadata wrapper with channel info
- Proper JSON encoding with `ensure_ascii=False` for international characters
- Indented with 2 spaces for readability

---

## 7. Processing Flow

### 7.1 Main Execution Flow

```
1. Initialize OAuth authentication
   ├─ Check for token.json
   ├─ Validate/refresh if needed
   └─ Launch browser flow if required

2. Prompt user for channel ID
   └─ Accept input from command line

3. Fetch channel information
   └─ API call: channels().list()

4. Extract all videos (paginated)
   ├─ Loop: Fetch playlist page
   │   ├─ Collect video IDs (max 50)
   │   ├─ Batch fetch video details
   │   └─ Process and store metadata
   └─ Continue until no nextPageToken

5. Save to dual formats
   ├─ Generate timestamped filenames
   ├─ Write CSV file
   └─ Write JSON file

6. Display success message
   └─ Show video count and channel name
```

### 7.2 Error Handling Strategy

**Principle**: Fail fast with informative error messages

**Exception Handling**:
```
try:
    channel_info = get_channel_info(youtube, channel_id)
    videos = get_all_videos(youtube, channel_info['uploads_playlist_id'])
    save_to_files(videos, channel_info['channel_name'])
    print(success_message)
except Exception as e:
    print(f"An error occurred: {e}")
```

**Common Error Scenarios**:
1. **Invalid Channel ID**: API returns empty items array
2. **Network Timeout**: Retry logic recommended (not implemented)
3. **Quota Exceeded**: HttpError 403 with quota message
4. **Authentication Failure**: Token refresh or re-authorization required

---

## 8. Duration Analysis Tool (Optional)

### 8.1 Purpose
Analyze total watch time of videos published within a specific time period (e.g., last year).

### 8.2 Functionality

**Input**: JSON file from main extraction tool

**Processing**:
1. Load JSON file
2. Filter videos by publish date (e.g., past 365 days)
3. Parse ISO 8601 duration for each video
4. Sum total seconds
5. Convert to human-readable format

**Output**:
```
Videos from the past year (since 2024-10-22): 487
Total duration: 328 hours, 45 minutes, 12 seconds
Total duration in days: 13.70 days
```

### 8.3 Date Handling
- Use timezone-aware datetime objects
- Parse ISO 8601 timestamps with timezone support
- Calculate relative dates from current UTC time

### 8.4 Known Limitation
Current implementation has hardcoded filename (line 6). Should be refactored to accept command-line argument or file selection.

---

## 9. Dependencies and Requirements

### 9.1 Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| google-auth-oauthlib | ^1.2.1 | OAuth 2.0 authentication flow |
| google-api-python-client | ^2.143.0 | YouTube Data API v3 client |
| Python | ^3.12 | Runtime environment |

### 9.2 Standard Library Dependencies
- `os`: File system operations and environment variables
- `csv`: CSV file writing with DictWriter
- `json`: JSON serialization/deserialization
- `datetime`: Timestamp handling and date arithmetic
- `re`: Regular expressions for duration parsing

### 9.3 Configuration Files

**Required**:
- `client_secret.json`: OAuth 2.0 credentials from Google Cloud Console
  - Download from: APIs & Services → Credentials
  - Type: OAuth 2.0 Client ID (Desktop app)
  - Must be gitignored

**Generated**:
- `token.json`: Stored OAuth credentials with refresh token
  - Auto-generated on first authentication
  - Auto-refreshed when expired
  - Must be gitignored

---

## 10. Security Considerations

### 10.1 Credential Management
- Never commit `client_secret.json` or `token.json` to version control
- Use `.gitignore` to exclude all `.json` files (includes output files)
- Store credentials outside repository for production deployments

### 10.2 OAuth Scope
The scope `youtube.force-ssl` is read-only for public data and user's private content. It does not allow:
- Uploading videos
- Deleting content
- Modifying channel settings

### 10.3 Development Security
`OAUTHLIB_INSECURE_TRANSPORT=1` allows OAuth over HTTP (localhost only). Never use in production.

---

## 11. Implementation Considerations

### 11.1 Performance Optimization
- Batch video detail requests (50 videos per API call) to minimize quota usage
- Process video data immediately rather than accumulating in memory
- Consider implementing progress indicators for large channels (1000+ videos)

### 11.2 Future Enhancements
1. **Progress Tracking**: Add progress bar or percentage indicator during extraction
2. **Incremental Updates**: Support fetching only new videos since last run
3. **Configurable Filters**: Filter by date range, view count, or duration
4. **Multiple Export Formats**: Add Excel, SQLite, or database export options
5. **Resumable Operations**: Save progress state to resume interrupted downloads
6. **Rate Limiting**: Implement intelligent throttling to avoid quota exhaustion
7. **Parallel Processing**: Concurrent API calls with request pooling

### 11.3 Testing Strategy
**Test Channel**: `UCW4Y4bPuafXwVEs0oly5vdw` (Mesele Ekonomi)
- 2000+ videos for pagination testing
- Turkish content for UTF-8 encoding validation
- Mix of public statistics and privacy settings

**Test Scenarios**:
1. Small channel (< 50 videos, single page)
2. Medium channel (50-500 videos, multiple pages)
3. Large channel (1000+ videos, extensive pagination)
4. Channel with videos missing statistics
5. Channel with videos lacking tags

---

## 12. API Reference Summary

### 12.1 YouTube Data API v3 Endpoints

**channels().list()**
```
Purpose: Get channel metadata and uploads playlist ID
Parts: contentDetails, snippet
Cost: 1 quota unit
Response: Channel object with relatedPlaylists.uploads
```

**playlistItems().list()**
```
Purpose: Get video IDs from uploads playlist
Parts: snippet
Parameters: playlistId, maxResults (1-50), pageToken
Cost: 1 quota unit
Response: Array of playlist items with video IDs
```

**videos().list()**
```
Purpose: Get full video metadata including statistics
Parts: snippet, contentDetails, statistics
Parameters: id (comma-separated, up to 50)
Cost: 1 quota unit
Response: Array of video objects with full metadata
```

### 12.2 Response Field Mapping

| API Field Path | Output Field | Data Type |
|---------------|--------------|-----------|
| id | video_id | string |
| snippet.title | title | string |
| snippet.description | description | string |
| snippet.publishedAt | publish_date | ISO 8601 string |
| snippet.categoryId | category_id | string |
| snippet.tags | tags | array |
| contentDetails.duration | duration | ISO 8601 string |
| statistics.viewCount | view_count | string or N/A |
| statistics.likeCount | like_count | string or N/A |
| statistics.commentCount | comment_count | string or N/A |

---

## 13. Glossary

**Channel ID**: 24-character identifier starting with "UC" (e.g., `UCW4Y4bPuafXwVEs0oly5vdw`)

**Uploads Playlist**: Special YouTube playlist containing all videos uploaded by a channel (ID starts with "UU")

**ISO 8601**: International standard for date/time and duration representation

**Quota Unit**: YouTube API's rate limiting currency (10,000 units per day per project)

**OAuth 2.0 Flow**: Three-legged authentication allowing application to access user data with consent

---

## 14. File Structure Overview

```
project/
├── main.py                 # Core extraction tool
├── analyze_duration.py     # Duration analysis utility
├── client_secret.json      # OAuth credentials (gitignored)
├── token.json             # Saved auth token (gitignored)
├── pyproject.toml         # Poetry dependency configuration
├── .gitignore             # Git exclusions (includes *.json)
└── output/
    ├── {channel}_{date}_{count}.csv   # Video data CSV
    └── {channel}_{date}_{count}.json  # Video data JSON
```

---

## 15. Quick Reference: Implementation Checklist

- [ ] Set up Google Cloud project and enable YouTube Data API v3
- [ ] Create OAuth 2.0 credentials (Desktop app type)
- [ ] Download `client_secret.json` to project directory
- [ ] Install dependencies: `google-auth-oauthlib`, `google-api-python-client`
- [ ] Implement OAuth flow with token caching
- [ ] Implement channel info retrieval
- [ ] Implement paginated video ID collection
- [ ] Implement batched video detail fetching
- [ ] Implement video data processing with optional field handling
- [ ] Implement CSV export with tag string conversion
- [ ] Implement JSON export with metadata wrapper
- [ ] Implement filename sanitization
- [ ] Add error handling for API failures
- [ ] Test with channels of varying sizes
- [ ] Implement duration parsing for analysis features (optional)
- [ ] Add `.gitignore` entries for credentials and tokens

---

**Document Version**: 1.0
**Date**: 2025-10-22
**Based on**: yt_videolist project implementation
