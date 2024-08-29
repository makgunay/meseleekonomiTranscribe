import os

class UserInterface:
    @staticmethod
    def get_audio_source():
        while True:
            choice = input("Enter '1' to use a local file or '2' to use a YouTube URL: ")
            if choice in ['1', '2']:
                return choice
            print("Invalid choice. Please enter '1' or '2'.")

    @staticmethod
    def get_local_file_path():
        while True:
            file_path = input("Enter the path to your local audio file: ")
            if os.path.isfile(file_path):
                return file_path
            print("File not found. Please try again.")

    @staticmethod
    def get_youtube_url():
        return input("Enter the YouTube video URL: ")

    @staticmethod
    def display_progress(message):
        print(message)

    @staticmethod
    def display_transcript(transcript):
        print("Transcript:")
        print(transcript)

    @staticmethod
    def display_error(error_message):
        print(f"Error: {error_message}")

    @staticmethod
    def display_success(message):
        print(f"Success: {message}")