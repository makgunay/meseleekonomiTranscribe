# MeseleEkonomi Transcribe

MeseleEkonomi Transcribe is a user-friendly tool that allows you to transcribe audio from local files or YouTube videos. This guide will help you set up and use the tool, even if you have no coding experience.

## What You Need Before Starting

1. A computer running macOS
2. Internet connection
3. Basic familiarity with using the Terminal app on macOS

## Setting Up Your Computer

Before you can use MeseleEkonomi Transcribe, you need to set up a few things on your computer. Don't worry, we'll guide you through each step!

### Step 1: Install Homebrew

Homebrew is a tool that helps install other software on your Mac. To install it:

1. Open the Terminal app on your Mac. You can find it by pressing Cmd + Space, typing "Terminal", and pressing Enter.
2. Copy and paste the following command into the Terminal and press Enter:

   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. Follow the prompts on the screen to complete the installation.

### Step 2: Install FFmpeg

FFmpeg is software that helps process audio and video files. To install it:

1. In the Terminal, type the following command and press Enter:

   ```
   brew install ffmpeg
   ```

2. Wait for the installation to complete.

### Step 3: Install Python

Python is the programming language used by MeseleEkonomi Transcribe. To install it:

1. In the Terminal, type the following command and press Enter:

   ```
   brew install python
   ```

2. Wait for the installation to complete.

### Step 4: Install Poetry

Poetry helps manage the project and its dependencies. To install it:

1. In the Terminal, type the following command and press Enter:

   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Wait for the installation to complete.

### Step 5: Install Git

Git is needed to download the Whisper model. To install it:

1. In the Terminal, type the following command and press Enter:

   ```
   brew install git
   ```

2. Wait for the installation to complete.

## Setting Up MeseleEkonomi Transcribe

Now that your computer is ready, let's set up the transcription tool:

1. Download the MeseleEkonomi Transcribe files from the provided source (your instructor or the project website should provide this).

2. Open the Terminal and navigate to the folder where you downloaded the files. For example, if you downloaded it to your Documents folder, you would type:

   ```
   cd ~/Documents/meseleekonomiTranscribe
   ```

3. Once you're in the correct folder, set up the project by typing:

   ```
   poetry install
   ```

   This may take a few minutes to complete.

4. Set up the Whisper model by running the following command:

   ```
   mkdir -p models/models--mlx-community--whisper-large-v2-mlx/
   ```

   This script will create the necessary directories the Whisper model.

   Go to https://huggingface.co/mlx-community/whisper-large-v2-mlx/tree/main and dowload the files to the created folder.

## Using MeseleEkonomi Transcribe

You're now ready to use the transcription tool! Here's how:

1. In the Terminal, make sure you're in the meseleekonomiTranscribe folder.

2. To start the web interface, type:

   ```
   poetry run streamlit run app.py
   ```

3. The web interface will open in your browser with three tabs:

   - **Local File**: Upload and transcribe local audio files
     * Supports MP3, WAV, M4A, and OGG formats
     * View transcript directly in browser
     * Download transcript as TXT and SRT files

   - **YouTube URL**: Transcribe YouTube videos
     * Enter a YouTube video URL
     * View transcript directly in browser
     * Files are saved automatically in the video directory

   - **Batch Processing**: Process multiple YouTube videos
     * Upload a CSV file with YouTube URLs in the third column
     * Monitor progress with a progress bar
     * Files are saved automatically for each video

4. For local files:
   - Upload your audio file using the file uploader
   - Click "Transcribe Local File"
   - View the transcript and download results

5. For YouTube videos:
   - Paste the video URL
   - Click "Transcribe YouTube Video"
   - View the transcript (files are saved automatically)

6. For batch processing:
   - Prepare a CSV file with YouTube URLs in the third column
   - Upload the CSV file
   - Click "Process Batch" and monitor progress

The tool will create:
- Text files (.txt) with plain transcripts
- SRT files (.srt) with timestamped segments

Example outputs are saved in these formats:

Text file:
```
Hello, welcome to our podcast.
Thank you for having me today.
Let's talk about our topic...
```

SRT file:
```
1
00:00:00,000 --> 00:00:02,500
Hello, welcome to our podcast.

2
00:00:02,500 --> 00:00:04,800
Thank you for having me today.

3
00:00:04,800 --> 00:00:07,200
Let's talk about our topic...
```

## Troubleshooting

If you encounter any issues:

- Make sure you've followed all the setup steps correctly.
- Check that you're in the correct folder when running commands.
- If you're using a local file, make sure you've typed the file path correctly.
- For YouTube videos, ensure you've entered the full URL correctly.

If you continue to have problems, please contact your instructor or the support team for assistance.

Happy transcribing!
# meseleekonomiTranscribe
