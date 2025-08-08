# MeseleEkonomi Transcribe

A powerful audio transcription tool that supports local files, YouTube videos, and batch processing with an intuitive web interface.

## Features

- **Multiple Input Sources**
  - Local audio files (MP3, WAV, M4A, OGG)
  - YouTube videos via URL
  - Batch processing from CSV files
  
- **Modern Web Interface**
  - Native file and folder selection dialogs
  - Dropdown menu for input source selection
  - Persistent output directory settings
  - Real-time progress tracking
  - Download buttons for transcripts
  
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
- Python 3.8 or higher
- FFmpeg
- Git

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
   - **Input Source**: Select from dropdown (Local File, YouTube URL, or Batch Processing)
   - **Language**: Choose Turkish or English
   - **Output Format**: Select desired output format(s)

4. **Process audio**:
   - **Local File**: Click "Select File" to choose audio file, then "Transcribe"
   - **YouTube URL**: Enter URL and click "Transcribe"
   - **Batch Processing**: Select CSV file with URLs and click "Process Batch"

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

## Batch Processing

For processing multiple YouTube videos:

1. Create a CSV file with URLs in the third column
2. Use the web interface's "Batch Processing" option
3. Select your CSV file using the native file picker
4. Monitor progress as each video is processed
5. All transcripts are saved to your output directory

## Project Structure

```
meseleekonomiTranscribe/
├── app.py                 # Streamlit web interface
├── main.py               # CLI interface
├── transcription.py      # Core transcription logic
├── audio_downloader.py   # YouTube download functionality
├── interface.py          # CLI user interface
├── utils.py             # Utility functions
├── models/              # MLX Whisper model files
└── video/              # Default output directory
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

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/makgunay/meseleekonomiTranscribe/issues).

Happy transcribing! 🎙️