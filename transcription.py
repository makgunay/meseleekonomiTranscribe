import os
import json
import mlx_whisper
from utils import format_timedelta
from datetime import timedelta
from interface import UserInterface

class Transcriber:
    def __init__(self):
        self.ui = UserInterface()

    def transcribe_audio(self, audio_file, language="tr"):
        try:
            # Get transcription with specified language (passed via decode_options)
            output = mlx_whisper.transcribe(
                audio_file, 
                path_or_hf_repo="./models/models--mlx-community--whisper-large-v2-mlx",
                language=language  # This gets passed to decode_options
            )
            if not output:
                return None
            return output
        except Exception as e:
            self.ui.display_error(f"An error occurred while transcribing: {str(e)}")
            return None

    def save_transcript(self, transcript, filename):
        output_file = f"{os.path.splitext(filename)[0]}_transcript.txt"
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                for segment in transcript['segments']:
                    file.write(f"{segment['text'].strip()}\n")
            self.ui.display_success(f"Transcript saved to {output_file}")
        except Exception as e:
            self.ui.display_error(f"An error occurred while saving the transcript: {str(e)}")

    def save_srt(self, segments, filename):
        output_file = f"{os.path.splitext(filename)[0]}.srt"
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                for i, segment in enumerate(segments, start=1):
                    start_time = timedelta(seconds=segment['start'])
                    end_time = timedelta(seconds=segment['end'])
                    file.write(f"{i}\n")
                    file.write(f"{format_timedelta(start_time)} --> {format_timedelta(end_time)}\n")
                    file.write(f"{segment['text'].strip()}\n\n")
            self.ui.display_success(f"SRT subtitles saved to {output_file}")
        except Exception as e:
            self.ui.display_error(f"An error occurred while saving the SRT file: {str(e)}")
    
    def save_json(self, transcript, filename):
        output_file = f"{os.path.splitext(filename)[0]}_transcript.json"
        try:
            json_data = {
                "text": transcript.get("text", ""),
                "segments": []
            }
            
            for segment in transcript.get("segments", []):
                json_data["segments"].append({
                    "id": segment.get("id"),
                    "start": segment.get("start"),
                    "end": segment.get("end"),
                    "text": segment.get("text", "").strip()
                })
            
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, ensure_ascii=False, indent=2)
            
            self.ui.display_success(f"JSON transcript saved to {output_file}")
        except Exception as e:
            self.ui.display_error(f"An error occurred while saving the JSON file: {str(e)}")
