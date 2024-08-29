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

2. To start the tool, type:

   ```
   poetry run python main.py
   ```

3. The tool will ask you if you want to transcribe a local file or a YouTube video. Type '1' for a local file or '2' for a YouTube video.

4. If you chose a local file, you'll need to provide the full path to the file. For example: `/Users/YourUsername/Documents/audio_file.mp3`

5. If you chose a YouTube video, you'll need to provide the full URL of the video.

6. The tool will then download the audio (if it's a YouTube video) and start transcribing. This may take a while depending on the length of the audio.

7. Once finished, the tool will show you the transcript and save it as a text file and an SRT file in the same folder as your audio file.

## Troubleshooting

If you encounter any issues:

- Make sure you've followed all the setup steps correctly.
- Check that you're in the correct folder when running commands.
- If you're using a local file, make sure you've typed the file path correctly.
- For YouTube videos, ensure you've entered the full URL correctly.

If you continue to have problems, please contact your instructor or the support team for assistance.

Happy transcribing!
# meseleekonomiTranscribe
