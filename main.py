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


def main():
    ui = UserInterface()

    audio_file = get_audio_file(ui)
    if not audio_file:
        ui.display_error("Failed to get audio file.")
        return

    ui.display_progress(f"Using audio file: {audio_file}")

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


if __name__ == "__main__":
    main()
