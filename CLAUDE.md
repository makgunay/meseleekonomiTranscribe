# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run the Streamlit Web Interface
```bash
poetry run streamlit run app.py
```

### Run CLI Interface
```bash
poetry run python main.py
```

### Install Dependencies
```bash
poetry install
```

## Architecture

This is a Python-based audio transcription application that uses MLX Whisper for transcription. The codebase has two entry points:

1. **Web Interface** (`app.py`) - Streamlit-based GUI with three tabs:
   - Local file upload and transcription
   - YouTube URL transcription
   - Batch processing from CSV files

2. **CLI Interface** (`main.py`) - Command-line interface for:
   - Local file transcription
   - YouTube video transcription
   - Batch processing from CSV

### Core Components

- **`transcription.py`**: Contains the `Transcriber` class that wraps MLX Whisper for audio transcription. Handles transcription, saving transcripts as TXT and SRT files.

- **`audio_downloader.py`**: Downloads audio from YouTube URLs using yt-dlp, converts to MP3 format.

- **`interface.py`**: Provides the `UserInterface` class for CLI interactions and user feedback.

- **`utils.py`**: Contains utility functions like `format_timedelta` for time formatting.

### Key Dependencies

- **mlx-whisper**: Local transcription model stored in `models/models--mlx-community--whisper-large-v2-mlx/`
- **yt-dlp**: YouTube video downloading
- **streamlit**: Web interface framework
- **poetry**: Dependency management

### Output Structure

- Transcripts are saved as `[filename]_transcript.txt` (plain text)
- Subtitles are saved as `[filename].srt` (timestamped segments)
- Default output directory: `./video/` (configurable in web interface)