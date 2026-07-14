import os
import glob
import yt_dlp
from interface import UserInterface

def download_audio(url, output_path='./video/', skip_existing=True):
    """
    Download audio from YouTube URL.

    Args:
        url: YouTube video URL
        output_path: Directory to save audio files
        skip_existing: If True, skip download if file already exists

    Returns:
        Path to audio file or None if download failed
    """
    ui = UserInterface()

    # Ensure output path exists
    os.makedirs(output_path, exist_ok=True)

    # First, extract video info without downloading to check for existing file
    if skip_existing:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_id = info.get('id', '')

                # Check if file with this video ID already exists
                existing_files = glob.glob(os.path.join(output_path, f'[{video_id}]*.mp3'))
                if existing_files:
                    ui.display_success(f"File already exists, skipping download: {existing_files[0]}")
                    return existing_files[0]
        except Exception as e:
            ui.display_error(f"Error checking for existing file: {str(e)}")
            # Continue with download attempt

    # Download configuration
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '[%(id)s] %(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            audio_file = os.path.splitext(filename)[0] + '.mp3'
            if os.path.exists(audio_file):
                ui.display_success(f"Audio downloaded successfully: {audio_file}")
                return audio_file
            else:
                ui.display_error(f"Audio file not found after download: {audio_file}")
                return None
    except yt_dlp.utils.DownloadError as e:
        ui.display_error(f"Download error: {str(e)}")
        return None
    except Exception as e:
        ui.display_error(f"An unexpected error occurred while downloading: {str(e)}")
        return None