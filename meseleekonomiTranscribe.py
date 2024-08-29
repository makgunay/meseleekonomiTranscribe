import mlx_whisper
import os
import yt_dlp
from datetime import timedelta

def download_audio(url, output_path='.'):
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
            return os.path.splitext(filename)[0] + '.mp3'
    except Exception as e:
        print(f"An error occurred while downloading: {str(e)}")
        return None

def transcribe_audio(audio_file):
    try:
        output = mlx_whisper.transcribe(audio_file)
        return output
    except Exception as e:
        print(f"An error occurred while transcribing: {str(e)}")
        return None

def save_transcript(transcript, filename):
    output_file = f"{os.path.splitext(filename)[0]}_transcript.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(transcript)
        print(f"Transcript saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving the transcript: {str(e)}")

def format_timedelta(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def save_srt(segments, filename):
    output_file = f"{os.path.splitext(filename)[0]}.srt"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            for i, segment in enumerate(segments, start=1):
                start_time = timedelta(seconds=segment['start'])
                end_time = timedelta(seconds=segment['end'])
                file.write(f"{i}\n")
                file.write(f"{format_timedelta(start_time)} --> {format_timedelta(end_time)}\n")
                file.write(f"{segment['text'].strip()}\n\n")
        print(f"SRT subtitles saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving the SRT file: {str(e)}")

def get_audio_file():
    while True:
        choice = input("Enter '1' to use a local file or '2' to use a YouTube URL: ")
        if choice == '1':
            file_path = input("Enter the path to your local audio file: ")
            if os.path.isfile(file_path):
                return file_path
            else:
                print("File not found. Please try again.")
        elif choice == '2':
            video_url = input("Enter the YouTube video URL: ")
            return download_audio(video_url)
        else:
            print("Invalid choice. Please enter '1' or '2'.")

def main():
    audio_file = get_audio_file()
    if not audio_file:
        return

    print(f"Using audio file: {audio_file}")

    # Transcribe audio
    transcription = transcribe_audio(audio_file)
    if not transcription:
        return

    # Print transcript
    print("Transcript:")
    print(transcription['text'])

    # Save transcript as text
    save_transcript(transcription['text'], audio_file)

    # Save transcript as SRT
    save_srt(transcription['segments'], audio_file)

if __name__ == "__main__":
    main()

help(mlx_whisper.transcribe)
