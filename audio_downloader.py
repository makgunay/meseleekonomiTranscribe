import os
import yt_dlp
from interface import UserInterface

def download_audio(url, output_path='./video/'):
    ui = UserInterface()
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path + '/%(title)s.%(ext)s',
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