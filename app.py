import streamlit as st
import os
import time
from transcription import Transcriber
import audio_downloader
import tempfile
from datetime import datetime
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

def main():
    st.title("MeseleEkonomi Transcribe 🎙️")
    st.write("Transcribe audio from local files or YouTube videos")

    # Status container for process feedback
    status_container = st.empty()
    progress_container = st.empty()
    time_container = st.empty()

    # Output directory selection with folder picker button
    if 'output_dir' not in st.session_state:
        st.session_state.output_dir = ''

    output_dir = st.text_input("Output Directory", 
                              value=st.session_state.get('output_dir', ''),
                              placeholder="Enter the path to save output files",
                              help="Enter the full path where you want to save the output files")
    
    if output_dir:
        st.session_state.output_dir = output_dir
    
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
            st.success(f"✅ Output directory set to: {output_dir}")
        except Exception as e:
            st.error(f"❌ Error creating output directory: {str(e)}")
            output_dir = None

    # Initialize transcriber
    transcriber = Transcriber()

    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Local File", "YouTube URL", "Batch Processing"])

    with tab1:
        st.header("Upload Local Audio File")
        uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'm4a', 'ogg'])
        
        if uploaded_file:
            if st.button("Transcribe Local File"):
                start_time = time.time()
                status_container.info("📝 Starting transcription process...")
                progress_bar = progress_container.progress(0)
                
                # Save uploaded file
                progress_bar.progress(10)
                status_container.info("💾 Saving uploaded file...")
                file_path = save_uploaded_file(uploaded_file, output_dir)
                
                if file_path:
                    # Transcribe
                    progress_bar.progress(30)
                    status_container.info("🎯 Transcribing audio...")
                    transcription_result = transcriber.transcribe_audio(file_path)
                    
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
                            
                            # Save transcript
                            transcript_path = f"{os.path.splitext(file_path)[0]}_transcript.txt"
                            transcriber.save_transcript(transcription_result, file_path)
                            with open(transcript_path, 'r', encoding='utf-8') as f:
                                transcript_content = f.read()
                            st.download_button(
                                "📄 Download Transcript (TXT)",
                                transcript_content,
                                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcript.txt"
                            )

                            # Save SRT
                            srt_path = f"{os.path.splitext(file_path)[0]}.srt"
                            transcriber.save_srt(transcription_result['segments'], file_path)
                            with open(srt_path, 'r', encoding='utf-8') as f:
                                srt_content = f.read()
                            st.download_button(
                                "🎬 Download Subtitles (SRT)",
                                srt_content,
                                file_name=f"{os.path.splitext(uploaded_file.name)[0]}.srt"
                            )

                            if not output_dir:
                                # Cleanup temporary files
                                try:
                                    os.unlink(file_path)
                                    os.unlink(transcript_path)
                                    os.unlink(srt_path)
                                except:
                                    pass
                                    
                            progress_bar.progress(100)
                            status_container.success("✅ Process completed successfully!")
                        except Exception as e:
                            st.error(f"❌ Error saving files: {str(e)}")
                    else:
                        status_container.error("❌ Transcription failed.")
                        progress_bar.empty()
                
                # Display total time taken
                end_time = time.time()
                time_container.info(f"⏱️ Total time: {format_time(end_time - start_time)}")

    with tab2:
        st.header("YouTube Video URL")
        youtube_url = st.text_input("Enter YouTube URL")
        
        if youtube_url:
            if st.button("Transcribe YouTube Video"):
                start_time = time.time()
                status_container.info("🚀 Starting YouTube processing...")
                progress_bar = progress_container.progress(0)
                
                # Download audio
                status_container.info("⬇️ Downloading YouTube video...")
                progress_bar.progress(20)
                output_path = output_dir if output_dir else './video/'
                audio_file = audio_downloader.download_audio(youtube_url, output_path)
                
                if audio_file:
                    # Transcribe
                    status_container.info("🎯 Transcribing audio...")
                    progress_bar.progress(50)
                    transcription_result = transcriber.transcribe_audio(audio_file)
                    
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
                            # Save transcript
                            transcript_path = f"{os.path.splitext(audio_file)[0]}_transcript.txt"
                            transcriber.save_transcript(transcription_result, audio_file)
                            
                            # Save SRT
                            srt_path = f"{os.path.splitext(audio_file)[0]}.srt"
                            transcriber.save_srt(transcription_result['segments'], audio_file)
                            
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

    with tab3:
        st.header("Batch Processing from CSV")
        st.write("Upload a CSV file with YouTube URLs (must have URLs in the third column)")
        uploaded_csv = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_csv:
            if st.button("Process Batch"):
                start_time = time.time()
                status_container.info("🚀 Starting batch processing...")
                
                # Save CSV file temporarily
                temp_csv_path = save_uploaded_file(uploaded_csv)
                if temp_csv_path:
                    try:
                        with open(temp_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                            import csv
                            reader = csv.reader(csvfile)
                            next(reader)  # Skip header
                            urls = [row[2] for row in reader if len(row) >= 3 and row[2]]
                            
                            if not urls:
                                status_container.error("❌ No valid URLs found in CSV file.")
                                return
                            
                            progress_bar = progress_container.progress(0)
                            status_text = st.empty()
                            
                            output_path = output_dir if output_dir else './video/'
                            for i, url in enumerate(urls):
                                status_container.info(f"🎯 Processing URL {i+1}/{len(urls)}")
                                status_text.text(f"Current URL: {url}")
                                
                                # Download and transcribe
                                audio_file = audio_downloader.download_audio(url, output_path)
                                if audio_file:
                                    transcription_result = transcriber.transcribe_audio(audio_file)
                                    if transcription_result:
                                        transcriber.save_transcript(transcription_result, audio_file)
                                        transcriber.save_srt(transcription_result['segments'], audio_file)
                                
                                progress_bar.progress((i + 1) / len(urls))
                            
                            status_text.empty()
                            progress_bar.progress(100)
                            status_container.success("✅ Batch processing completed!")
                            st.success(f"📁 Processed {len(urls)} files. Files saved to: {output_path}")
                    except Exception as e:
                        status_container.error(f"❌ Error processing batch: {str(e)}")
                    finally:
                        try:
                            os.unlink(temp_csv_path)
                        except:
                            pass
                
                # Display total time taken
                end_time = time.time()
                time_container.info(f"⏱️ Total time: {format_time(end_time - start_time)}")

if __name__ == "__main__":
    main()
