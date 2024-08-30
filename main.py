import audio_downloader
import transcription
from interface import UserInterface


def get_audio_file(ui):
    choice = ui.get_audio_source()
    if choice == '1':
        return ui.get_local_file_path()
    elif choice == '2':
        video_url = ui.get_youtube_url()
        ui.display_progress("Downloading audio from YouTube...")
        return audio_downloader.download_audio(video_url)
    elif choice == '3':
        csv_file = ui.get_csv_file_path()
        return csv_file


def process_single_file(ui, audio_file):
    ui.display_progress(f"Processing audio file: {audio_file}")

    # Transcribe audio
    ui.display_progress("Transcribing audio...")
    transcription_result = transcription.transcribe_audio(audio_file)
    if not transcription_result:
        ui.display_error("Transcription failed.")
        return

    # Display transcript
    ui.display_transcript(transcription_result['text'])

    # Save transcript as text
    transcription.save_transcript(transcription_result['text'], audio_file)
    ui.display_success(f"Transcript saved as text file.")

    # Save transcript as SRT
    transcription.save_srt(transcription_result['segments'], audio_file)
    ui.display_success(f"Transcript saved as SRT file.")


def main():
    ui = UserInterface()

    audio_source = get_audio_file(ui)
    if not audio_source:
        ui.display_error("Failed to get audio source.")
        return

    if audio_source.endswith('.csv'):
        # Batch processing
        csv_data = ui.read_csv_file(audio_source)
        if not csv_data:
            ui.display_error("Failed to read CSV file.")
            return
        
        for row in csv_data:
            if len(row) >= 3:
                video_url = row[2]
                ui.display_progress(f"Processing URL: {video_url}")
                audio_file = audio_downloader.download_audio(video_url)
                if audio_file:
                    process_single_file(ui, audio_file)
                else:
                    ui.display_error(f"Failed to download audio for URL: {video_url}")
    else:
        # Single file processing
        process_single_file(ui, audio_source)


if __name__ == "__main__":
    main()
