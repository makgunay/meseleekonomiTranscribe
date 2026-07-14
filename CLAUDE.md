# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run the Streamlit Web Interface
```bash
uv run streamlit run app.py
```

### Run CLI Interface
```bash
uv run python main.py
```

### Run Channel Extractor (CLI)
```bash
uv run python channel_extractor.py
```

### Install Dependencies
```bash
uv sync
```

### Testing and Code Quality
There is currently no test suite, and pytest/black/flake8 are **not** installed (there is no dev-dependency group in `pyproject.toml`). To use them, first add them:
```bash
uv add --dev pytest black flake8
```

## Architecture

This is a Python-based audio transcription application that uses MLX Whisper for transcription. The codebase has three entry points:

1. **Web Interface** (`app.py`) - Streamlit-based GUI with an "Input Source" selector (`app.py:207`) offering four modes:
   - Local file upload and transcription
   - YouTube URL transcription
   - Batch processing from CSV files
   - Channel Extractor (NEW) - Extract all videos from a YouTube channel

2. **CLI Interface** (`main.py`) - Command-line interface for:
   - Local file transcription
   - YouTube video transcription
   - Batch processing from CSV

3. **Channel Extractor** (`channel_extractor.py`) - Standalone tool for:
   - Extracting all videos from a YouTube channel using YouTube Data API v3
   - Generating CSV and JSON files with video metadata
   - Tracking download status with a 'downloaded' flag

### Core Components

- **`transcription.py`**: Contains the `Transcriber` class that wraps MLX Whisper for audio transcription. Handles transcription, saving transcripts as TXT and SRT files.

- **`audio_downloader.py`**: Downloads audio from YouTube URLs using yt-dlp, converts to MP3 format at 192kbps. Includes skip_existing feature to avoid re-downloading files.

- **`channel_extractor.py`**: Extracts comprehensive video metadata from YouTube channels using YouTube Data API v3. Implements OAuth 2.0 authentication, paginated video fetching, and dual-format export (CSV + JSON).

- **`interface.py`**: Provides the `UserInterface` class for CLI interactions and user feedback.

- **`utils.py`**: Contains utility functions like `format_timedelta` for time formatting.

### Key Dependencies

- **mlx-whisper**: Local transcription model stored in `models/models--mlx-community--whisper-large-v2-mlx/`
  - Model must be downloaded from Hugging Face before first use
  - Path is hardcoded in `transcription.py:17`
- **yt-dlp**: YouTube video downloading with automatic retry mechanisms
- **streamlit**: Web interface framework
- **google-auth-oauthlib** & **google-api-python-client**: YouTube Data API v3 integration for channel extraction
- **uv**: Dependency management (Python >=3.12, <3.14)

### Platform-Specific Features

- **macOS**: Native Finder dialogs for file/folder selection using AppleScript (`app.py:49-116`)
- **Other platforms**: Fallback to tkinter dialogs

### Output Structure

- **Text format**: `[filename]_transcript.txt` - Plain text, one segment per line
- **SRT format**: `[filename].srt` - Timestamped subtitle segments
- **JSON format**: `[filename]_transcript.json` - Full transcript with detailed segment metadata
- Default output directory: `./video/` (configurable in web interface)
- Output format can be selected individually or in combination via the web UI

## Gotchas

- **deno required for YouTube downloads**: yt-dlp 2026.x needs a JavaScript runtime to extract YouTube formats; without deno, only thumbnails are visible and downloads fail with "Requested format is not available". Install with `brew install deno`. Also, do not pass a hardcoded `player_client` in `extractor_args` — client requirements change and yt-dlp's defaults are maintained upstream.
- **Model download required on fresh clone**: `models/` is gitignored. Download with:
  ```bash
  huggingface-cli download mlx-community/whisper-large-v2-mlx \
    --local-dir ./models/models--mlx-community--whisper-large-v2-mlx
  ```
- **uv only**: This project migrated from Poetry to uv (July 2026). `uv.lock` is the only lock file and is checked in; do not reintroduce `poetry.lock` or `[tool.poetry]` sections in `pyproject.toml`. The project is marked `package = false` under `[tool.uv]` (flat script app, not an installable package).

## CSV Format for Batch Processing

### Manual CSV Format (Legacy)

- The CSV must include a header row
- YouTube URLs must be in the third column (index 2)
- Empty or malformed rows are ignored by the UI
- Processing is sequential, not parallel

Example:

```csv
title,channel,url
Konutta şehir efsanesi,Mesele Ekonomi,https://www.youtube.com/watch?v=lX42-MSQ_rM
2025 beklentileri,Mesele Ekonomi,https://www.youtube.com/watch?v=UuXCEDwVKMI
```

### Channel Extractor CSV Format (Recommended)

The Channel Extractor generates CSV files with comprehensive metadata and a download tracking flag:

**Required columns:**
- `video_id`: YouTube video ID (11 characters)
- `title`: Video title
- `description`: Full video description
- `link`: YouTube watch URL (column 4, index 3)
- `publish_date`: ISO 8601 timestamp
- `view_count`, `like_count`, `comment_count`: Statistics (may be 'N/A')
- `duration`: ISO 8601 duration format (e.g., PT4M33S)
- `tags`: Comma-separated tag list
- `category_id`: YouTube category ID
- `downloaded`: Download status flag ("Yes", "No", "Failed")

**Folder structure:**
- Channel data saved to: `{output_dir}/{channel_name}/`
- Filename format: `{channel_name}_{YYYYMMDD_HHMM}_{video_count}.csv`

**Download tracking:**
- "No": Not yet downloaded
- "Yes": Successfully downloaded
- "Failed": Download failed
- The batch downloader automatically updates this flag

Example:

```csv
video_id,title,description,link,publish_date,view_count,like_count,comment_count,duration,tags,category_id,downloaded
dQw4w9WgXcQ,Never Gonna Give You Up,Official music video,https://www.youtube.com/watch?v=dQw4w9WgXcQ,2009-10-25T06:57:33Z,1500000000,25000000,3500000,PT3M33S,"music, 80s",10,No
```

## Channel Extractor Setup

### Prerequisites

1. **Google Cloud Project with YouTube Data API v3 enabled**
2. **OAuth 2.0 credentials** (`client_secret.json`)

### Setup Steps

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable "YouTube Data API v3" in the API Library

2. **Create OAuth 2.0 Credentials**:
   - Navigate to: APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Desktop app"
   - Download the credentials as `client_secret.json`

3. **Place credentials file**:
   - Put `client_secret.json` in the project root directory
   - Add to `.gitignore` (already configured)

4. **First-time authentication**:
   - Run the channel extractor (CLI or Web UI)
   - Browser will open for Google account authorization
   - Grant access to YouTube Data API
   - Token will be saved to `token.json` for future use

### API Quota

- Daily quota: 10,000 units
- Cost per channel extraction (1000 videos): ~41 units
- Large channel (2000 videos): ~81 units (0.81% of daily quota)

### Workflow

1. **Extract Channel**: Use Channel Extractor to create CSV/JSON files
2. **Download Videos**: Use the generated CSV with batch downloader
3. **Transcribe**: Process downloaded videos with transcription features

## GitHub Integration

This repository includes a Claude Code GitHub Action (`.github/workflows/claude.yml`) that responds to:
- Issues (opened, edited)
- Issue comments
- Pull requests (opened, synchronize, reopened)
- PR review comments

Requires `CLAUDE_API_KEY` secret to be configured in the repository settings.