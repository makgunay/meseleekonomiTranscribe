import streamlit as st
import os
import time
from transcription import Transcriber
import audio_downloader
import tempfile
import subprocess
import platform
import csv
from channel_extractor import ChannelExtractor

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

def save_outputs(transcriber, transcription_result, audio_file, output_format):
    """Save the selected output formats next to the audio file.

    Returns a list of (label, path, download_filename) for the files written."""
    entries = []
    base = os.path.splitext(audio_file)[0]
    name = os.path.basename(base)

    if output_format in ["All Formats", "Text Only", "Text + JSON"]:
        transcriber.save_transcript(transcription_result, audio_file)
        entries.append(("Download transcript (TXT)", f"{base}_transcript.txt", f"{name}_transcript.txt"))

    if output_format in ["All Formats", "SRT Only", "SRT + JSON"]:
        transcriber.save_srt(transcription_result['segments'], audio_file)
        entries.append(("Download subtitles (SRT)", f"{base}.srt", f"{name}.srt"))

    if output_format in ["All Formats", "JSON Only", "Text + JSON", "SRT + JSON"]:
        transcriber.save_json(transcription_result, audio_file)
        entries.append(("Download transcript (JSON)", f"{base}_transcript.json", f"{name}_transcript.json"))

    return entries

def render_last_result(input_source):
    """Render the most recent transcription result.

    Lives outside the button handlers so the transcript and its download
    buttons survive Streamlit reruns (every widget interaction reruns the
    script, and button state only lasts a single run)."""
    result = st.session_state.get('last_result')
    if not result or result['mode'] != input_source:
        return

    st.divider()
    st.subheader("Transcript")
    st.caption(f"{result['source']} · {result['duration']} · saved to {result['output_dir']}")
    st.text_area("Full transcript", result['text'], height=300, key="last_result_text")

    files = [f for f in result['files'] if os.path.exists(f[1])]
    if files:
        cols = st.columns(len(files))
        for col, (label, path, filename) in zip(cols, files):
            with open(path, 'r', encoding='utf-8') as f:
                col.download_button(label, f.read(), file_name=filename, key=f"dl_{filename}")

def main():
    st.logo("MeseleEkonomi_1.png", size="large")
    st.title("MeseleEkonomi Transcribe")
    st.write("Transcribe audio from local files or YouTube videos")

    # Initialize session state for persistent output directory
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = './video/'

    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None

    if 'selected_csv' not in st.session_state:
        st.session_state.selected_csv = None

    if 'downloaded_files' not in st.session_state:
        st.session_state.downloaded_files = []

    if 'batch_download_complete' not in st.session_state:
        st.session_state.batch_download_complete = False

    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

    with st.sidebar:
        st.header("Settings")

        output_dir = st.text_input("Output directory",
                                  value=st.session_state.output_dir,
                                  placeholder="Enter path or browse to select a folder",
                                  help="Full path where output files are saved",
                                  key="output_dir_input")
        if st.button("Browse…", key="browse_main", help="Choose a folder in Finder"):
            selected_folder = select_folder_native()
            if selected_folder:
                st.session_state.output_dir = selected_folder
                st.rerun()

        # Update session state if manually entered
        if output_dir != st.session_state.output_dir:
            st.session_state.output_dir = output_dir

        # Verify output directory quietly; only failure needs attention
        if st.session_state.output_dir:
            try:
                os.makedirs(st.session_state.output_dir, exist_ok=True)
                st.caption(f"Saving to {st.session_state.output_dir}")
            except Exception as e:
                st.error(f"Cannot create output directory: {str(e)}")
                st.session_state.output_dir = None

        input_source = st.selectbox("Input source",
                                   ["Local File", "YouTube URL", "Batch Processing (CSV)", "Channel Extractor"],
                                   key="input_source")

        language_choice = st.selectbox("Language",
                                      ["Turkish", "English"],
                                      key="language_select")
        language = 'tr' if language_choice == "Turkish" else 'en'

        output_format = st.selectbox("Output format",
                                    ["All Formats", "Text Only", "SRT Only", "JSON Only", "Text + JSON", "SRT + JSON"],
                                    key="output_format")

    # Initialize transcriber
    transcriber = Transcriber()

    # Display interface based on selected input source
    if input_source == "Local File":
        st.header("Local audio file")

        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            st.text_input("Selected file",
                          value=st.session_state.selected_file or "No file selected",
                          disabled=True)

        with col2:
            if st.button("Select file…", key="select_file_btn"):
                selected_file = select_file_native()
                if selected_file:
                    st.session_state.selected_file = selected_file
                    st.rerun()

        if st.session_state.selected_file and os.path.exists(st.session_state.selected_file):
            if st.button("Transcribe", type="primary", key="transcribe_local"):
                start_time = time.time()
                file_path = st.session_state.selected_file

                with st.status("Transcribing…", expanded=True) as status:
                    st.write(f"Transcribing audio ({language_choice})…")
                    transcription_result = transcriber.transcribe_audio(file_path, language=language)

                    if transcription_result:
                        st.write("Saving output files…")
                        try:
                            # Ensure output directory exists
                            output_path = st.session_state.output_dir or './video/'
                            os.makedirs(output_path, exist_ok=True)

                            # Copy file to output directory if it's not already there
                            output_file_path = os.path.join(output_path, os.path.basename(file_path))
                            if file_path != output_file_path:
                                import shutil
                                shutil.copy2(file_path, output_file_path)
                                file_path = output_file_path

                            files = save_outputs(transcriber, transcription_result, file_path, output_format)
                            elapsed = format_time(time.time() - start_time)
                            st.session_state.last_result = {
                                'mode': "Local File",
                                'source': os.path.basename(file_path),
                                'text': transcription_result['text'],
                                'files': files,
                                'output_dir': output_path,
                                'duration': elapsed,
                            }
                            status.update(label=f"Transcription complete ({elapsed})",
                                          state="complete", expanded=False)
                        except Exception as e:
                            status.update(label="Saving failed", state="error")
                            st.error(f"Could not save output files: {str(e)}")
                    else:
                        status.update(label="Transcription failed", state="error")
                        st.error("Transcription failed — confirm the file is a supported audio "
                                 "format and check the terminal for details.")

    elif input_source == "YouTube URL":
        st.header("YouTube video")
        youtube_url = st.text_input("YouTube URL", key="youtube_url_input")

        if youtube_url:
            if st.button("Transcribe", type="primary", key="transcribe_youtube"):
                start_time = time.time()

                with st.status("Transcribing…", expanded=True) as status:
                    st.write("Downloading audio from YouTube…")
                    output_path = st.session_state.output_dir or './video/'
                    audio_file = audio_downloader.download_audio(youtube_url, output_path)

                    if audio_file:
                        st.write(f"Transcribing audio ({language_choice})…")
                        transcription_result = transcriber.transcribe_audio(audio_file, language=language)

                        if transcription_result:
                            st.write("Saving output files…")
                            try:
                                files = save_outputs(transcriber, transcription_result, audio_file, output_format)
                                elapsed = format_time(time.time() - start_time)
                                st.session_state.last_result = {
                                    'mode': "YouTube URL",
                                    'source': os.path.basename(audio_file),
                                    'text': transcription_result['text'],
                                    'files': files,
                                    'output_dir': os.path.dirname(audio_file),
                                    'duration': elapsed,
                                }
                                status.update(label=f"Transcription complete ({elapsed})",
                                              state="complete", expanded=False)
                            except Exception as e:
                                status.update(label="Saving failed", state="error")
                                st.error(f"Could not save output files: {str(e)}")
                        else:
                            status.update(label="Transcription failed", state="error")
                            st.error("Transcription failed — the audio downloaded but could not "
                                     "be transcribed. Check the terminal for details.")
                    else:
                        status.update(label="Download failed", state="error")
                        st.error("Could not download this video — check the URL and your "
                                 "connection. yt-dlp output is in the terminal.")

    elif input_source == "Batch Processing (CSV)":
        st.header("Batch processing")
        st.write("Select a CSV file with YouTube URLs (URLs should be in the third column)")
        with st.expander("CSV format requirements", expanded=True):
            st.markdown(
                "- The CSV must include a header row\n"
                "- YouTube URLs must be in the third column (index 2)\n"
                "- Empty or malformed rows are ignored"
            )
            st.code(
                "title,channel,url\n"
                "Konutta şehir efsanesi,Mesele Ekonomi,https://www.youtube.com/watch?v=lX42-MSQ_rM\n"
                "2025 beklentileri,Mesele Ekonomi,https://www.youtube.com/watch?v=UuXCEDwVKMI\n",
                language="csv"
            )

        # Processing mode selection
        processing_mode = st.radio(
            "Processing mode",
            ["Sequential — download and transcribe one video at a time",
             "Download first — download everything, then transcribe"],
            key="batch_processing_mode",
            help="Download-first mode fetches all audio up front and waits for you before transcribing."
        )

        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            st.text_input("Selected CSV",
                          value=st.session_state.selected_csv or "No file selected",
                          disabled=True)

        with col2:
            if st.button("Select CSV…", key="select_csv_btn"):
                selected_csv = select_csv_native()
                if selected_csv:
                    st.session_state.selected_csv = selected_csv
                    st.rerun()

        if st.session_state.selected_csv and os.path.exists(st.session_state.selected_csv):
            # Preview CSV content
            urls = []
            try:
                with open(st.session_state.selected_csv, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    if len(rows) > 1:
                        urls = [row[2] for row in rows[1:] if len(row) >= 3 and row[2]]
                        st.info(f"Found {len(urls)} URLs in CSV file")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

            # Sequential mode (original behavior)
            if processing_mode.startswith("Sequential"):
                if st.button("Download and transcribe all", type="primary", key="process_batch_sequential"):
                    start_time = time.time()

                    if urls:
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        output_path = st.session_state.output_dir or './video/'
                        successful = 0
                        failed = 0

                        for i, url in enumerate(urls):
                            status_text.text(f"Processing {i+1}/{len(urls)}: {url}")

                            # Download and transcribe
                            audio_file = audio_downloader.download_audio(url, output_path)
                            if audio_file:
                                transcription_result = transcriber.transcribe_audio(audio_file, language=language)
                                if transcription_result:
                                    save_outputs(transcriber, transcription_result, audio_file, output_format)
                                    successful += 1
                                else:
                                    failed += 1
                            else:
                                failed += 1

                            progress_bar.progress((i + 1) / len(urls))

                        status_text.empty()
                        st.success(f"Batch complete in {format_time(time.time() - start_time)}: "
                                   f"{successful} transcribed, {failed} failed. Files saved to {output_path}")
                    else:
                        st.error("No valid URLs found in the CSV file — check that URLs are in the third column.")

            # Download-first mode
            else:
                # Phase 1: Download all videos
                if not st.session_state.batch_download_complete:
                    if st.button("Download all videos", type="primary", key="download_all_videos"):
                        start_time = time.time()

                        if urls:
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            output_path = st.session_state.output_dir or './video/'
                            downloaded_files = []
                            failed_downloads = 0

                            for i, url in enumerate(urls):
                                status_text.text(f"Downloading {i+1}/{len(urls)}: {url}")

                                audio_file = audio_downloader.download_audio(url, output_path)
                                if audio_file:
                                    downloaded_files.append(audio_file)
                                else:
                                    failed_downloads += 1

                                progress_bar.progress((i + 1) / len(urls))

                            status_text.empty()

                            # Store downloaded files in session state
                            st.session_state.downloaded_files = downloaded_files
                            st.session_state.batch_download_complete = True

                            st.success(f"Downloaded {len(downloaded_files)} files in "
                                       f"{format_time(time.time() - start_time)}, {failed_downloads} failed.")

                            st.rerun()
                        else:
                            st.error("No valid URLs found in the CSV file — check that URLs are in the third column.")

                # Phase 2: Transcribe all downloaded videos
                else:
                    st.info(f"{len(st.session_state.downloaded_files)} videos are downloaded and ready for transcription.")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Transcribe downloaded videos", type="primary", key="start_transcription"):
                            start_time = time.time()

                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            successful = 0
                            failed = 0
                            downloaded_files = st.session_state.downloaded_files

                            for i, audio_file in enumerate(downloaded_files):
                                status_text.text(f"Transcribing {i+1}/{len(downloaded_files)}: {os.path.basename(audio_file)}")

                                transcription_result = transcriber.transcribe_audio(audio_file, language=language)
                                if transcription_result:
                                    save_outputs(transcriber, transcription_result, audio_file, output_format)
                                    successful += 1
                                else:
                                    failed += 1

                                progress_bar.progress((i + 1) / len(downloaded_files))

                            status_text.empty()
                            st.success(f"Batch complete in {format_time(time.time() - start_time)}: "
                                       f"{successful} transcribed, {failed} failed. Files saved to "
                                       f"{st.session_state.output_dir or './video/'}")

                            # Reset state
                            st.session_state.downloaded_files = []
                            st.session_state.batch_download_complete = False

                    with col_b:
                        if st.button("Reset and start over", key="reset_batch"):
                            st.session_state.downloaded_files = []
                            st.session_state.batch_download_complete = False
                            st.rerun()

    elif input_source == "Channel Extractor":
        st.header("Channel extractor")
        st.write("Extract all videos from a YouTube channel and create a CSV file for batch processing")

        with st.expander("How to use", expanded=True):
            st.markdown(
                "1. Enter a YouTube channel ID (format: UCxxxxxxxxxxxxxxxxxx)\n"
                "2. Click 'Extract channel data' to fetch all videos\n"
                "3. Data will be saved as CSV and JSON in a channel-specific folder\n"
                "4. The CSV will include a 'downloaded' flag for tracking\n"
                "5. Use the generated CSV with the 'Batch Processing (CSV)' input source"
            )
            st.info("First-time setup: You'll need to authenticate with Google OAuth. This requires `client_secret.json` from Google Cloud Console.")

        # Initialize extractor session state
        if 'channel_extracted' not in st.session_state:
            st.session_state.channel_extracted = False
        if 'channel_csv_path' not in st.session_state:
            st.session_state.channel_csv_path = None
        if 'channel_folder' not in st.session_state:
            st.session_state.channel_folder = None

        # Channel ID input
        channel_id = st.text_input(
            "YouTube channel ID",
            placeholder="UCW4Y4bPuafXwVEs0oly5vdw",
            help="Enter the channel ID (starts with UC, typically 24 characters)",
            key="channel_id_input"
        )

        if st.button("Extract channel data", type="primary", key="extract_channel", disabled=not channel_id):
            if not channel_id.startswith("UC") or len(channel_id) != 24:
                st.warning("Channel ID should start with 'UC' and be 24 characters long")
            else:
                start_time = time.time()

                with st.status("Extracting channel data…", expanded=True) as status:
                    try:
                        # Initialize extractor
                        extractor = ChannelExtractor()
                        extractor.base_output_path = st.session_state.output_dir or './video/'

                        # Authenticate
                        st.write("Authenticating with YouTube API…")
                        if not extractor.authenticate():
                            status.update(label="Authentication failed", state="error")
                            st.error("Authentication failed — check that client_secret.json exists "
                                     "in the project root and is valid.")
                        else:
                            # Get channel info
                            st.write("Fetching channel information…")
                            channel_info = extractor.get_channel_info(channel_id)

                            if not channel_info:
                                status.update(label="Channel not found", state="error")
                                st.error("Channel not found — check the channel ID.")
                            else:
                                st.write(f"Fetching all videos from '{channel_info['channel_name']}'…")
                                videos = extractor.get_all_videos(channel_info['uploads_playlist_id'])

                                if videos:
                                    st.write("Saving channel data…")
                                    csv_path, json_path = extractor.save_channel_data(
                                        videos, channel_info['channel_name']
                                    )

                                    # Update session state
                                    st.session_state.channel_extracted = True
                                    st.session_state.channel_csv_path = csv_path
                                    st.session_state.channel_folder = os.path.dirname(csv_path)

                                    elapsed = format_time(time.time() - start_time)
                                    status.update(label=f"Extracted {len(videos)} videos from "
                                                        f"'{channel_info['channel_name']}' ({elapsed})",
                                                  state="complete", expanded=False)
                                else:
                                    status.update(label="No videos found", state="error")
                                    st.error("No videos found for this channel — check the channel ID "
                                             "and the terminal for API errors.")

                    except Exception as e:
                        import traceback
                        print(traceback.format_exc())
                        status.update(label="Extraction failed", state="error")
                        st.error(f"Extraction failed: {str(e)}. Full details are in the terminal.")

        # Show batch download option if extraction is complete
        if st.session_state.channel_extracted and st.session_state.channel_csv_path:
            st.divider()
            st.subheader("Download videos from channel")

            csv_path = st.session_state.channel_csv_path
            folder_path = st.session_state.channel_folder

            st.caption(f"Channel CSV: {csv_path}")

            # Read CSV to show stats
            try:
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    total_videos = len(rows)
                    downloaded_count = sum(1 for row in rows if row.get('downloaded', '').lower() == 'yes')

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total videos", total_videos)
                    with col2:
                        st.metric("Downloaded", downloaded_count)
                    with col3:
                        st.metric("Remaining", total_videos - downloaded_count)
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

            if st.button("Download all videos", type="primary", key="download_channel_videos"):
                start_time = time.time()

                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    with open(csv_path, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)

                    # Create live metric display
                    metrics_container = st.empty()

                    downloaded = 0
                    skipped = 0
                    failed = 0

                    # Count initial downloaded
                    initial_downloaded = sum(1 for row in rows if row.get('downloaded', '').lower() == 'yes')
                    downloaded = initial_downloaded
                    skipped = initial_downloaded

                    # Get fieldnames from first row for CSV writing
                    fieldnames = list(rows[0].keys()) if rows else []

                    # Update each row with download status
                    for i, row in enumerate(rows):
                        url = row.get('link', '')
                        video_title = row.get('title', 'Unknown')

                        # Update live metrics
                        with metrics_container.container():
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Downloaded", downloaded, delta=f"+{downloaded - initial_downloaded}")
                            with col2:
                                st.metric("Skipped", skipped)
                            with col3:
                                st.metric("Failed", failed)
                            with col4:
                                st.metric("Remaining", len(rows) - i)

                        status_text.text(f"Processing {i+1}/{len(rows)}: {video_title[:50]}")

                        # Skip if already downloaded
                        if row.get('downloaded', '').lower() == 'yes':
                            # Already counted in initial_downloaded
                            pass
                        else:
                            # Download audio
                            audio_file = audio_downloader.download_audio(url, folder_path, skip_existing=True)

                            if audio_file:
                                row['downloaded'] = 'Yes'
                                downloaded += 1
                            else:
                                row['downloaded'] = 'Failed'
                                failed += 1

                            # Save CSV after each download attempt
                            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(rows)

                        progress_bar.progress((i + 1) / len(rows))

                    status_text.empty()
                    st.success(f"Download complete in {format_time(time.time() - start_time)}: "
                               f"{downloaded} downloaded, {skipped} skipped, {failed} failed.")

                except Exception as e:
                    progress_bar.empty()
                    st.error(f"Batch download failed: {str(e)}")

            # Reset button
            if st.button("Extract another channel", key="reset_channel"):
                st.session_state.channel_extracted = False
                st.session_state.channel_csv_path = None
                st.session_state.channel_folder = None
                st.rerun()

    # Persistent result display for single-item modes
    render_last_result(input_source)

if __name__ == "__main__":
    main()
