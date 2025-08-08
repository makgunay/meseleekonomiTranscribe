import streamlit as st
import os
import time
from transcription import Transcriber
import audio_downloader
import tempfile
from datetime import datetime
from pathlib import Path
import subprocess
import platform
import csv

st.set_page_config(
    page_title="MeseleEkonomi Transcribe",
    page_icon="🎙️",
    layout="wide"
)

def save_uploaded_file(uploaded_file, output_dir=None):
    """Save uploaded file to a temporary location or specified directory and return the path"""
    try:
        if output_dir:
            # Save to specified directory
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            return file_path
        else:
            # Save to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                return tmp_file.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {str(e)}")
        return None

def format_time(seconds):
    """Format time duration in a human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def select_folder_native():
    """Open native folder picker dialog using AppleScript on macOS"""
    try:
        if platform.system() == 'Darwin':  # macOS
            # Use AppleScript to open native folder picker
            script = '''
            tell application "System Events"
                activate
                set folderPath to choose folder with prompt "Select output folder for transcriptions"
                return POSIX path of folderPath
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                folder_path = result.stdout.strip()
                return folder_path
            else:
                return None
        else:
            # Fallback for non-macOS systems - use tkinter
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.attributes('-topmost', True)  # Bring to front
            folder_path = filedialog.askdirectory(title="Select output folder for transcriptions")
            root.destroy()
            return folder_path if folder_path else None
    except Exception as e:
        st.error(f"Error opening folder picker: {str(e)}")
        return None

def select_file_native(file_types=[('Audio Files', '*.mp3 *.wav *.m4a *.ogg'), ('All Files', '*.*')]):
    """Open native file picker dialog"""
    try:
        if platform.system() == 'Darwin':  # macOS
            # Use AppleScript to open native file picker
            script = '''
            tell application "System Events"
                activate
                set audioFile to choose file with prompt "Select audio file to transcribe" of type {"mp3", "wav", "m4a", "ogg", "public.audio"}
                return POSIX path of audioFile
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                file_path = result.stdout.strip()
                return file_path
            else:
                return None
        else:
            # Fallback for non-macOS systems - use tkinter
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.attributes('-topmost', True)  # Bring to front
            file_path = filedialog.askopenfilename(
                title="Select audio file to transcribe",
                filetypes=file_types
            )
            root.destroy()
            return file_path if file_path else None
    except Exception as e:
        st.error(f"Error opening file picker: {str(e)}")
        return None

def select_csv_native():
    """Open native file picker dialog for CSV files"""
    try:
        if platform.system() == 'Darwin':  # macOS
            # Use AppleScript to open native file picker for CSV
            script = '''
            tell application "System Events"
                activate
                set csvFile to choose file with prompt "Select CSV file with YouTube URLs" of type {"csv", "public.comma-separated-values-text"}
                return POSIX path of csvFile
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                file_path = result.stdout.strip()
                return file_path
            else:
                return None
        else:
            # Fallback for non-macOS systems - use tkinter
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.attributes('-topmost', True)  # Bring to front
            file_path = filedialog.askopenfilename(
                title="Select CSV file with YouTube URLs",
                filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
            )
            root.destroy()
            return file_path if file_path else None
    except Exception as e:
        st.error(f"Error opening file picker: {str(e)}")
        return None

def main():
    st.title("MeseleEkonomi Transcribe 🎙️")
    st.write("Transcribe audio from local files or YouTube videos")

    # Initialize session state for persistent output directory
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = './video/'
    
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None
    
    if 'selected_csv' not in st.session_state:
        st.session_state.selected_csv = None

    # Status containers
    status_container = st.empty()
    progress_container = st.empty()
    time_container = st.empty()

    st.subheader("Settings")
    
    # First row: Output directory with browser
    col1, col2 = st.columns([4, 1])
    with col1:
        output_dir = st.text_input("Output Directory", 
                                  value=st.session_state.output_dir,
                                  placeholder="Enter path or click Browse to select folder",
                                  help="Enter the full path where you want to save the output files",
                                  key="output_dir_input")
    with col2:
        st.write("")  # Empty space for alignment
        st.write("")  # Empty space for alignment
        if st.button("📂 Browse", key="browse_main", help="Open Finder to select folder"):
            selected_folder = select_folder_native()
            if selected_folder:
                st.session_state.output_dir = selected_folder
                st.rerun()
    
    # Update session state if manually entered
    if output_dir != st.session_state.output_dir:
        st.session_state.output_dir = output_dir
    
    # Second row: Input source, Language and Output Format
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_source = st.selectbox("Input Source", 
                                   ["Local File", "YouTube URL", "Batch Processing (CSV)"],
                                   key="input_source")
    
    with col2:
        language_choice = st.selectbox("Language", 
                                      ["Turkish", "English"],
                                      key="language_select")
        language = 'tr' if language_choice == "Turkish" else 'en'
    
    with col3:
        output_format = st.selectbox("Output Format", 
                                    ["All Formats", "Text Only", "SRT Only", "JSON Only", "Text + JSON", "SRT + JSON"],
                                    key="output_format")
    
    # Verify output directory
    if st.session_state.output_dir:
        try:
            os.makedirs(st.session_state.output_dir, exist_ok=True)
            st.success(f"✅ Output directory: {st.session_state.output_dir}")
        except Exception as e:
            st.error(f"❌ Error creating output directory: {str(e)}")
            st.session_state.output_dir = None

    # Initialize transcriber
    transcriber = Transcriber()

    st.divider()

    # Display interface based on selected input source
    if input_source == "Local File":
        st.header("Local Audio File")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Display selected file if any
            if st.session_state.selected_file:
                st.text_input("Selected File", value=st.session_state.selected_file, disabled=True)
            else:
                st.text_input("Selected File", value="No file selected", disabled=True)
        
        with col2:
            st.write("")  # Empty space for alignment
            st.write("")  # Empty space for alignment
            if st.button("📄 Select File", key="select_file_btn"):
                selected_file = select_file_native()
                if selected_file:
                    st.session_state.selected_file = selected_file
                    st.rerun()
        
        if st.session_state.selected_file and os.path.exists(st.session_state.selected_file):
            if st.button("🎯 Transcribe", type="primary", key="transcribe_local"):
                start_time = time.time()
                status_container.info("📝 Starting transcription process...")
                progress_bar = progress_container.progress(0)
                
                file_path = st.session_state.selected_file
                
                # Transcribe
                progress_bar.progress(30)
                status_container.info(f"🎯 Transcribing audio (Language: {language_choice})...")
                transcription_result = transcriber.transcribe_audio(file_path, language=language)
                
                if transcription_result:
                    progress_bar.progress(70)
                    status_container.info("📊 Processing results...")
                    
                    # Display results
                    st.success("✨ Transcription completed!")
                    st.subheader("Transcript")
                    st.text_area("Full Transcript", transcription_result['text'], height=300)
                    
                    # Save and offer downloads
                    try:
                        progress_bar.progress(90)
                        status_container.info("💾 Saving output files...")
                        
                        # Ensure output directory exists
                        output_path = st.session_state.output_dir or './video/'
                        os.makedirs(output_path, exist_ok=True)
                        
                        # Copy file to output directory if it's not already there
                        output_file_path = os.path.join(output_path, os.path.basename(file_path))
                        if file_path != output_file_path:
                            import shutil
                            shutil.copy2(file_path, output_file_path)
                            file_path = output_file_path
                        
                        # Save files based on selected format
                        if output_format in ["All Formats", "Text Only", "Text + JSON"]:
                            transcript_path = f"{os.path.splitext(file_path)[0]}_transcript.txt"
                            transcriber.save_transcript(transcription_result, file_path)
                            with open(transcript_path, 'r', encoding='utf-8') as f:
                                transcript_content = f.read()
                            st.download_button(
                                "📄 Download Transcript (TXT)",
                                transcript_content,
                                file_name=f"{os.path.splitext(os.path.basename(file_path))[0]}_transcript.txt"
                            )

                        if output_format in ["All Formats", "SRT Only", "SRT + JSON"]:
                            srt_path = f"{os.path.splitext(file_path)[0]}.srt"
                            transcriber.save_srt(transcription_result['segments'], file_path)
                            with open(srt_path, 'r', encoding='utf-8') as f:
                                srt_content = f.read()
                            st.download_button(
                                "🎬 Download Subtitles (SRT)",
                                srt_content,
                                file_name=f"{os.path.splitext(os.path.basename(file_path))[0]}.srt"
                            )
                        
                        if output_format in ["All Formats", "JSON Only", "Text + JSON", "SRT + JSON"]:
                            json_path = f"{os.path.splitext(file_path)[0]}_transcript.json"
                            transcriber.save_json(transcription_result, file_path)
                            with open(json_path, 'r', encoding='utf-8') as f:
                                json_content = f.read()
                            st.download_button(
                                "📊 Download Transcript (JSON)",
                                json_content,
                                file_name=f"{os.path.splitext(os.path.basename(file_path))[0]}_transcript.json"
                            )
                            
                        progress_bar.progress(100)
                        status_container.success(f"✅ Files saved to: {output_path}")
                    except Exception as e:
                        st.error(f"❌ Error saving files: {str(e)}")
                else:
                    status_container.error("❌ Transcription failed.")
                    progress_bar.empty()
                
                # Display total time taken
                end_time = time.time()
                time_container.info(f"⏱️ Total time: {format_time(end_time - start_time)}")

    elif input_source == "YouTube URL":
        st.header("YouTube Video")
        youtube_url = st.text_input("Enter YouTube URL", key="youtube_url_input")
        
        if youtube_url:
            if st.button("🎯 Transcribe", type="primary", key="transcribe_youtube"):
                start_time = time.time()
                status_container.info("🚀 Starting YouTube processing...")
                progress_bar = progress_container.progress(0)
                
                # Download audio
                status_container.info("⬇️ Downloading YouTube video...")
                progress_bar.progress(20)
                output_path = st.session_state.output_dir or './video/'
                audio_file = audio_downloader.download_audio(youtube_url, output_path)
                
                if audio_file:
                    # Transcribe
                    status_container.info(f"🎯 Transcribing audio (Language: {language_choice})...")
                    progress_bar.progress(50)
                    transcription_result = transcriber.transcribe_audio(audio_file, language=language)
                    
                    if transcription_result:
                        # Display results
                        progress_bar.progress(80)
                        status_container.info("📊 Processing results...")
                        st.success("✨ Transcription completed!")
                        st.subheader("Transcript")
                        st.text_area("Full Transcript", transcription_result['text'], height=300)
                        
                        # Save files
                        try:
                            status_container.info("💾 Saving output files...")
                            # Save files based on selected format
                            if output_format in ["All Formats", "Text Only", "Text + JSON"]:
                                transcriber.save_transcript(transcription_result, audio_file)
                            
                            if output_format in ["All Formats", "SRT Only", "SRT + JSON"]:
                                transcriber.save_srt(transcription_result['segments'], audio_file)
                            
                            if output_format in ["All Formats", "JSON Only", "Text + JSON", "SRT + JSON"]:
                                transcriber.save_json(transcription_result, audio_file)
                            
                            progress_bar.progress(100)
                            status_container.success(f"✅ Files saved to: {os.path.dirname(audio_file)}")
                        except Exception as e:
                            st.error(f"❌ Error saving files: {str(e)}")
                    else:
                        status_container.error("❌ Transcription failed.")
                        progress_bar.empty()
                else:
                    status_container.error("❌ Failed to download YouTube video.")
                    progress_bar.empty()
                
                # Display total time taken
                end_time = time.time()
                time_container.info(f"⏱️ Total time: {format_time(end_time - start_time)}")

    elif input_source == "Batch Processing (CSV)":
        st.header("Batch Processing")
        st.write("Select a CSV file with YouTube URLs (URLs should be in the third column)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Display selected CSV file if any
            if st.session_state.selected_csv:
                st.text_input("Selected CSV", value=st.session_state.selected_csv, disabled=True)
            else:
                st.text_input("Selected CSV", value="No file selected", disabled=True)
        
        with col2:
            st.write("")  # Empty space for alignment
            st.write("")  # Empty space for alignment
            if st.button("📋 Select CSV", key="select_csv_btn"):
                selected_csv = select_csv_native()
                if selected_csv:
                    st.session_state.selected_csv = selected_csv
                    st.rerun()
        
        if st.session_state.selected_csv and os.path.exists(st.session_state.selected_csv):
            # Preview CSV content
            try:
                with open(st.session_state.selected_csv, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    if len(rows) > 1:
                        urls = [row[2] for row in rows[1:] if len(row) >= 3 and row[2]]
                        st.info(f"Found {len(urls)} URLs in CSV file")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
                urls = []
            
            if st.button("🎯 Process Batch", type="primary", key="process_batch"):
                start_time = time.time()
                status_container.info("🚀 Starting batch processing...")
                
                if urls:
                    progress_bar = progress_container.progress(0)
                    status_text = st.empty()
                    
                    output_path = st.session_state.output_dir or './video/'
                    successful = 0
                    failed = 0
                    
                    for i, url in enumerate(urls):
                        status_container.info(f"🎯 Processing URL {i+1}/{len(urls)}")
                        status_text.text(f"Current URL: {url}")
                        
                        # Download and transcribe
                        audio_file = audio_downloader.download_audio(url, output_path)
                        if audio_file:
                            transcription_result = transcriber.transcribe_audio(audio_file, language=language)
                            if transcription_result:
                                # Save files based on selected format
                                if output_format in ["All Formats", "Text Only", "Text + JSON"]:
                                    transcriber.save_transcript(transcription_result, audio_file)
                                
                                if output_format in ["All Formats", "SRT Only", "SRT + JSON"]:
                                    transcriber.save_srt(transcription_result['segments'], audio_file)
                                
                                if output_format in ["All Formats", "JSON Only", "Text + JSON", "SRT + JSON"]:
                                    transcriber.save_json(transcription_result, audio_file)
                                
                                successful += 1
                            else:
                                failed += 1
                        else:
                            failed += 1
                        
                        progress_bar.progress((i + 1) / len(urls))
                    
                    status_text.empty()
                    progress_bar.progress(100)
                    status_container.success("✅ Batch processing completed!")
                    st.success(f"📁 Processed {successful} files successfully, {failed} failed. Files saved to: {output_path}")
                else:
                    status_container.error("❌ No valid URLs found in CSV file.")
                
                # Display total time taken
                end_time = time.time()
                time_container.info(f"⏱️ Total time: {format_time(end_time - start_time)}")

if __name__ == "__main__":
    main()