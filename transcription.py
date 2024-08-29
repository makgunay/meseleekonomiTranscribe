import os
import mlx_whisper
from utils import format_timedelta
from datetime import timedelta
from interface import UserInterface

def transcribe_audio(audio_file):
    ui = UserInterface()
    try:
        output = mlx_whisper.transcribe(audio_file, path_or_hf_repo="./models/models--mlx-community--whisper-large-v2-mlx")
        return output
    except Exception as e:
        ui.display_error(f"An error occurred while transcribing: {str(e)}")
        return None

def save_transcript(transcript, filename):
    ui = UserInterface()
    output_file = f"{os.path.splitext(filename)[0]}_transcript.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(transcript)
        ui.display_success(f"Transcript saved to {output_file}")
    except Exception as e:
        ui.display_error(f"An error occurred while saving the transcript: {str(e)}")

def save_srt(segments, filename):
    ui = UserInterface()
    output_file = f"{os.path.splitext(filename)[0]}.srt"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            for i, segment in enumerate(segments, start=1):
                start_time = timedelta(seconds=segment['start'])
                end_time = timedelta(seconds=segment['end'])
                file.write(f"{i}\n")
                file.write(f"{format_timedelta(start_time)} --> {format_timedelta(end_time)}\n")
                file.write(f"{segment['text'].strip()}\n\n")
        ui.display_success(f"SRT subtitles saved to {output_file}")
    except Exception as e:
        ui.display_error(f"An error occurred while saving the SRT file: {str(e)}")