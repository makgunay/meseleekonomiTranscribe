# MeseleEkonomi Transcribe

A powerful audio transcription tool that supports local files, YouTube videos, and batch processing with an intuitive web interface.

## Features

- **Multiple Input Sources**
  - Local audio files (MP3, WAV, M4A, OGG)
  - YouTube videos via URL
  - Batch processing from CSV files
  - Channel Extractor - Extract all videos from a YouTube channel
  
- **Modern Web Interface**
  - Native file and folder selection dialogs
  - Dropdown menu for input source selection
  - Persistent output directory settings
  - Real-time progress tracking with live metrics
  - Download buttons for transcripts
  - YouTube Data API v3 integration with OAuth 2.0
  
- **Multiple Output Formats**
  - Plain text transcripts (.txt)
  - SRT subtitles with timestamps (.srt)
  - JSON format with detailed segments (.json)
  - Flexible format selection (individual or combined)

- **Language Support**
  - Turkish transcription
  - English transcription
  - Automatic language detection

## Prerequisites

- macOS (with native Finder integration) or Linux/Windows
- Python 3.12 or higher
- FFmpeg
- Git
- **For Channel Extractor**: Google Cloud Project with YouTube Data API v3 enabled (see setup below)

## Installation

### macOS Setup

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install required dependencies**:
   ```bash
   brew install ffmpeg python git
   ```

3. **Install Poetry** (dependency manager):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. **Clone the repository**:
   ```bash
   git clone https://github.com/makgunay/meseleekonomiTranscribe.git
   cd meseleekonomiTranscribe
   ```

5. **Install project dependencies**:
   ```bash
   poetry install
   ```

6. **Download the Whisper model**:
   ```bash
   mkdir -p models/models--mlx-community--whisper-large-v2-mlx/
   ```
   Then download the model files from [Hugging Face](https://huggingface.co/mlx-community/whisper-large-v2-mlx/tree/main) and place them in the created folder.

## Usage

### Web Interface (Recommended)

1. **Start the application**:
   ```bash
   poetry run streamlit run app.py
   ```

2. **Access the interface**:
   - Open your browser at `http://localhost:8501`
   - The interface will display with settings and input options

3. **Configure settings**:
   - **Output Directory**: Click "Browse" to select via Finder or enter path manually
   - **Input Source**: Select from dropdown (Local File, YouTube URL, Batch Processing, or Channel Extractor)
   - **Language**: Choose Turkish or English
   - **Output Format**: Select desired output format(s)

4. **Process audio**:
   - **Local File**: Click "Select File" to choose audio file, then "Transcribe"
   - **YouTube URL**: Enter URL and click "Transcribe"
   - **Batch Processing**: Select CSV file with URLs and click "Process Batch"
   - **Channel Extractor**: Enter channel ID to extract all videos and download/transcribe

### Command Line Interface

For command-line usage:
```bash
poetry run python main.py
```

Follow the prompts to:
1. Choose input source (local file or YouTube URL)
2. Select language (Turkish or English)
3. Choose output format
4. Enter file path or URL

## Output Files

The tool generates different output formats based on your selection:

### Text Format (.txt)
Plain text transcript without timestamps:
```
Hello, welcome to our podcast.
Thank you for having me today.
Let's talk about our topic...
```

### SRT Format (.srt)
Subtitle format with timestamps:
```
1
00:00:00,000 --> 00:00:02,500
Hello, welcome to our podcast.

2
00:00:02,500 --> 00:00:04,800
Thank you for having me today.
```

### JSON Format (.json)
Detailed segment information with timestamps and confidence scores:
```json
{
  "text": "Full transcript text...",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, welcome to our podcast."
    }
  ]
}
```

## Channel Extractor

Extract all videos from a YouTube channel using YouTube Data API v3.

### Setup

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
   - It's automatically excluded from git via .gitignore

4. **First-time authentication**:
   - Run the channel extractor (CLI or Web UI)
   - Browser will open for Google account authorization
   - Grant access to YouTube Data API
   - Token will be saved to `token.json` for future use

### Usage

1. Find the YouTube channel ID (the part starting with "UC" in the channel URL)
2. In the web interface, select "Channel Extractor" from the input source dropdown
3. Enter the channel ID and click "Extract Channel Data"
4. The tool will:
   - Authenticate with YouTube API
   - Extract all videos from the channel
   - Save CSV and JSON files with comprehensive metadata
   - Mark already downloaded videos in the CSV
5. Use the generated CSV with "Batch Processing" to download and transcribe videos

### API Quota

- Daily quota: 10,000 units
- Cost per channel extraction (~1000 videos): ~41 units
- Large channel (2000 videos): ~81 units (0.81% of daily quota)

## Batch Processing

For processing multiple YouTube videos:

### Option 1: Channel Extractor (Recommended)

1. Use the Channel Extractor to generate a CSV with all channel videos
2. The CSV includes comprehensive metadata and download tracking
3. Use the generated CSV with Batch Processing
4. The system automatically:
   - Skips already downloaded videos
   - Updates CSV with download status after each video
   - Shows live metrics (downloaded, skipped, failed, remaining)

### Option 2: Manual CSV

1. Create a CSV file with URLs in the third column
2. Use the web interface's "Batch Processing" option
3. Select your CSV file using the native file picker
4. Monitor progress as each video is processed
5. All transcripts are saved to your output directory

### CSV Format

#### Channel Extractor CSV Format (Recommended)

The Channel Extractor generates CSV files with comprehensive metadata:

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
- Channel data saved to: `video/{channel_name}/`
- Filename format: `{channel_name}_{YYYYMMDD_HHMM}_{video_count}.csv`

**Download tracking:**
- "No": Not yet downloaded
- "Yes": Successfully downloaded
- "Failed": Download failed
- The batch downloader automatically updates this flag in real-time

Example:

```csv
video_id,title,description,link,publish_date,view_count,like_count,comment_count,duration,tags,category_id,downloaded
dQw4w9WgXcQ,Never Gonna Give You Up,Official music video,https://www.youtube.com/watch?v=dQw4w9WgXcQ,2009-10-25T06:57:33Z,1500000000,25000000,3500000,PT3M33S,"music, 80s",10,No
```

#### Manual CSV Format (Legacy)

- The CSV must include a header row
- YouTube URLs must be in the third column (index 2)
- Empty or malformed rows are ignored

Example:

```csv
title,channel,url
Konutta şehir efsanesi,Mesele Ekonomi,https://www.youtube.com/watch?v=lX42-MSQ_rM
2025 beklentileri,Mesele Ekonomi,https://www.youtube.com/watch?v=UuXCEDwVKMI
```

## Project Structure

```
meseleekonomiTranscribe/
├── app.py                 # Streamlit web interface
├── main.py                # CLI interface
├── channel_extractor.py   # YouTube Data API v3 integration
├── transcription.py       # Core transcription logic
├── audio_downloader.py    # YouTube download functionality
├── interface.py           # CLI user interface
├── utils.py               # Utility functions
├── models/                # MLX Whisper model files
├── video/                 # Default output directory
│   └── {channel_name}/    # Channel-specific folders
├── client_secret.json     # OAuth credentials (not in git)
└── token.json             # OAuth token (not in git)
```

## Troubleshooting

### Common Issues

1. **YouTube download errors**: 
   - The tool includes automatic retry mechanisms
   - Uses latest yt-dlp with enhanced extraction methods
   - If persistent, check your internet connection

2. **Model not found**:
   - Ensure model files are in `models/models--mlx-community--whisper-large-v2-mlx/`
   - Download all required files from Hugging Face

3. **Permission errors**:
   - Ensure you have write permissions for the output directory
   - Try selecting a different output folder

4. **Memory issues**:
   - For long audio files, the tool processes in segments
   - Close other applications if needed

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Style
```bash
poetry run black .
poetry run flake8
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- MLX Whisper for the transcription model
- Streamlit for the web framework
- yt-dlp for YouTube downloading capabilities
- Google YouTube Data API v3 for channel extraction

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/makgunay/meseleekonomiTranscribe/issues).

Happy transcribing! 🎙️