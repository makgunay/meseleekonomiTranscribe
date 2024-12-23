import streamlit as st
import os
from transcription import Transcriber
import audio_downloader
import tempfile

st.set_page_config(
    page_title="MeseleEkonomi Transcribe",
    page_icon="🎙️",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location and return the path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {str(e)}")
        return None

def main():
    st.title("MeseleEkonomi Transcribe 🎙️")
    st.write("Transcribe audio from local files or YouTube videos")

    # Initialize transcriber
    transcriber = Transcriber()

    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Local File", "YouTube URL", "Batch Processing"])

    with tab1:
        st.header("Upload Local Audio File")
        uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'm4a', 'ogg'])
        
        if uploaded_file:
            if st.button("Transcribe Local File"):
                with st.spinner("Processing audio file..."):
                    # Save uploaded file
                    temp_path = save_uploaded_file(uploaded_file)
                    if temp_path:
                        # Transcribe
                        transcription_result = transcriber.transcribe_audio(temp_path)
                        if transcription_result:
                            # Display results
                            st.success("Transcription completed!")
                            st.subheader("Transcript")
                            st.text_area("Full Transcript", transcription_result['text'], height=300)
                            
                            # Save and offer downloads
                            try:
                                # Save transcript
                                transcript_path = f"{os.path.splitext(temp_path)[0]}_transcript.txt"
                                transcriber.save_transcript(transcription_result, temp_path)
                                with open(transcript_path, 'r', encoding='utf-8') as f:
                                    transcript_content = f.read()
                                st.download_button(
                                    "Download Transcript (TXT)",
                                    transcript_content,
                                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcript.txt"
                                )

                                # Save SRT
                                srt_path = f"{os.path.splitext(temp_path)[0]}.srt"
                                transcriber.save_srt(transcription_result['segments'], temp_path)
                                with open(srt_path, 'r', encoding='utf-8') as f:
                                    srt_content = f.read()
                                st.download_button(
                                    "Download Subtitles (SRT)",
                                    srt_content,
                                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}.srt"
                                )
                            except Exception as e:
                                st.error(f"Error saving files: {str(e)}")
                            
                            # Cleanup
                            try:
                                os.unlink(temp_path)
                                os.unlink(transcript_path)
                                os.unlink(srt_path)
                            except:
                                pass
                        else:
                            st.error("Transcription failed.")

    with tab2:
        st.header("YouTube Video URL")
        youtube_url = st.text_input("Enter YouTube URL")
        
        if youtube_url:
            if st.button("Transcribe YouTube Video"):
                with st.spinner("Downloading and processing YouTube video..."):
                    # Download audio
                    audio_file = audio_downloader.download_audio(youtube_url)
                    if audio_file:
                        # Transcribe
                        transcription_result = transcriber.transcribe_audio(audio_file)
                        if transcription_result:
                            # Display results
                            st.success("Transcription completed!")
                            st.subheader("Transcript")
                            st.text_area("Full Transcript", transcription_result['text'], height=300)
                            
                            # Save and offer downloads
                            try:
                                # Save transcript
                                transcript_path = f"{os.path.splitext(audio_file)[0]}_transcript.txt"
                                transcriber.save_transcript(transcription_result, audio_file)
                                with open(transcript_path, 'r', encoding='utf-8') as f:
                                    transcript_content = f.read()
                                # Save SRT
                                srt_path = f"{os.path.splitext(audio_file)[0]}.srt"
                                transcriber.save_srt(transcription_result['segments'], audio_file)
                                with open(srt_path, 'r', encoding='utf-8') as f:
                                    srt_content = f.read()              
                            except Exception as e:
                                st.error(f"Error saving files: {str(e)}")
                        else:
                            st.error("Transcription failed.")
                    else:
                        st.error("Failed to download YouTube video.")

    with tab3:
        st.header("Batch Processing from CSV")
        st.write("Upload a CSV file with YouTube URLs (must have URLs in the third column)")
        uploaded_csv = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_csv:
            if st.button("Process Batch"):
                # Save CSV file
                temp_csv_path = save_uploaded_file(uploaded_csv)
                if temp_csv_path:
                    try:
                        with open(temp_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                            import csv
                            reader = csv.reader(csvfile)
                            next(reader)  # Skip header
                            urls = [row[2] for row in reader if len(row) >= 3 and row[2]]
                            
                            if not urls:
                                st.error("No valid URLs found in CSV file.")
                                return
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, url in enumerate(urls):
                                status_text.text(f"Processing URL {i+1}/{len(urls)}: {url}")
                                
                                # Download and transcribe
                                audio_file = audio_downloader.download_audio(url)
                                if audio_file:
                                    transcription_result = transcriber.transcribe_audio(audio_file)
                                    if transcription_result:
                                        transcriber.save_transcript(transcription_result, audio_file)
                                        transcriber.save_srt(transcription_result['segments'], audio_file)
                                
                                progress_bar.progress((i + 1) / len(urls))
                            
                            status_text.text("Batch processing completed!")
                            st.success(f"Processed {len(urls)} files. Check the output directory for results.")
                    except Exception as e:
                        st.error(f"Error processing batch: {str(e)}")
                    finally:
                        try:
                            os.unlink(temp_csv_path)
                        except:
                            pass

if __name__ == "__main__":
    main()
