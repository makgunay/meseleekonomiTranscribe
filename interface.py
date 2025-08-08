import os
import csv

class UserInterface:
    @staticmethod
    def get_audio_source():
        while True:
            choice = input("Enter '1' to use a local file, '2' to use a YouTube URL, or '3' for batch transcription from CSV: ")
            if choice in ['1', '2', '3']:
                return choice
            print("Invalid choice. Please enter '1', '2', or '3'.")

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
    def get_csv_file_path():
        while True:
            file_path = input("Enter the path to your CSV file: ")
            if os.path.isfile(file_path):
                return file_path
            print("File not found. Please try again.")

    @staticmethod
    def read_csv_file(file_path):
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row
                return [row for row in reader if len(row) >= 3 and row[2]]
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return None

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
    
    @staticmethod
    def get_output_format():
        while True:
            choice = input("Choose output format - '1' for Text, '2' for SRT, '3' for JSON, '4' for All formats: ")
            if choice in ['1', '2', '3', '4']:
                return choice
            print("Invalid choice. Please enter '1', '2', '3', or '4'.")
    
    @staticmethod
    def get_language():
        while True:
            choice = input("Select input language - '1' for Turkish, '2' for English: ")
            if choice == '1':
                return 'tr'
            elif choice == '2':
                return 'en'
            print("Invalid choice. Please enter '1' for Turkish or '2' for English.")