import streamlit as st
import os
from dubbing_utils import FanarAPIClient, extract_audio_from_video, save_text_to_file, load_text_from_file, combine_audio_video
from dotenv import load_dotenv
import re
from pydub import AudioSegment
import subprocess
import glob
from pytubefix import YouTube
from pytubefix.cli import on_progress
import shutil

def separate_music_with_demucs(audio_file, output_dir='demucs_output'):
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        'demucs', '--two-stems=vocals', '-o', output_dir, audio_file
    ]
    subprocess.run(cmd, check=True)
    # Find the model subfolder (e.g., htdemucs)
    model_dir = next(
        d for d in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, d))
    )
    # Search for no_vocals.wav in all subfolders
    search_path = os.path.join(output_dir, model_dir, '*', 'no_vocals.wav')
    matches = glob.glob(search_path)
    if not matches:
        raise FileNotFoundError(f"No 'no_vocals.wav' found in {search_path}")
    return matches[0]

def mix_music_and_tts(music_path, tts_path, output_path):
    music = AudioSegment.from_file(music_path)
    tts = AudioSegment.from_file(tts_path)
    # Lower music volume for clarity
    music = music - 10
    # Overlay TTS on music
    mixed = music.overlay(tts)
    mixed.export(output_path, format='wav')

def download_youtube_video(url, output_path="downloaded_youtube_video.mp4"):
    """Download a YouTube video and return the path to the downloaded file using pytubefix."""
    try:
        # Basic URL validation
        if not url or 'youtube.com' not in url and 'youtu.be' not in url:
            raise ValueError("Please provide a valid YouTube URL")
            
        # Clean up URL (remove extra parameters)
        if '&' in url:
            url = url.split('&')[0]
            
        yt = YouTube(url, on_progress_callback=on_progress)
        
        # Show video info
        try:
            st.info(f"Video Title: {yt.title}")
            st.info(f"Duration: {yt.length} seconds")
        except:
            st.info("Video info loading...")
        
        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()
        if not stream:
            raise RuntimeError("No suitable video stream found")
        st.info(f"Downloading: {stream.resolution} quality")
        
        # Download the video
        stream.download(filename=output_path)
        
        # Verify the file was downloaded
        if not os.path.exists(output_path):
            raise RuntimeError("Download completed but file not found")
            
        # Get file size
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        st.info(f"Download completed! File size: {file_size:.2f} MB")
            
        return output_path
    except Exception as e:
        error_msg = str(e)
        if "HTTP Error 400" in error_msg:
            raise RuntimeError("YouTube API error. This might be due to region restrictions or video availability. Try a different video or check if the video is publicly available.")
        elif "Video unavailable" in error_msg:
            raise RuntimeError("This video is not available for download. It might be private, age-restricted, or region-blocked.")
        else:
            raise RuntimeError(f"Failed to download YouTube video: {error_msg}")

def get_audio_duration(audio_file):
    """Get the duration of an audio file in seconds."""
    try:
        audio = AudioSegment.from_file(audio_file)
        return len(audio) / 1000  # Convert milliseconds to seconds
    except Exception as e:
        st.warning(f"Could not determine audio duration: {e}")
        return None

def select_transcription_model(audio_duration):
    """Select the appropriate transcription model based on audio duration."""
    if audio_duration is None:
        # Default to short-form model if duration cannot be determined
        return "Fanar-Aura-STT-1"
    
    # Use long-form model for audio longer than 30 seconds
    if audio_duration > 30:
        return "Fanar-Aura-STT-1"
    else:
        return "Fanar-Aura-STT-1"

def get_video_title(input_video_path, youtube_url=None):
    """Extract video title from YouTube URL or use filename for uploaded videos."""
    if youtube_url:
        try:
            yt = YouTube(youtube_url)
            if yt.title and yt.title.strip():
                return yt.title.strip()
        except Exception as e:
            st.warning(f"Could not extract YouTube title: {e}")
    
    # For uploaded videos, use the filename without extension
    if input_video_path:
        base_name = os.path.splitext(os.path.basename(input_video_path))[0]
        # Remove common prefixes/suffixes
        base_name = base_name.replace("uploaded_video", "").replace("downloaded_youtube_video", "")
        if base_name.strip():
            return base_name.strip()
    
    return "video"

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename

def cleanup_temp_files(temp_files_list, keep_final_video=True):
    """Clean up temporary files after processing."""
    cleaned_files = []
    for file_path in temp_files_list:
        if os.path.exists(file_path):
            try:
                # Don't delete the final video if keep_final_video is True
                if keep_final_video and file_path.endswith('.mp4') and 'arabic dub' in file_path:
                    continue
                    
                os.remove(file_path)
                cleaned_files.append(file_path)
            except Exception as e:
                st.warning(f"Could not remove {file_path}: {e}")
    
    if cleaned_files:
        st.info(f"🧹 Cleaned up {len(cleaned_files)} temporary files")
    
    return cleaned_files

def cleanup_demucs_output():
    """Clean up Demucs output directory."""
    demucs_dir = "demucs_output"
    if os.path.exists(demucs_dir):
        try:
            shutil.rmtree(demucs_dir)
            st.info("🧹 Cleaned up Demucs output directory")
        except Exception as e:
            st.warning(f"Could not remove Demucs directory: {e}")

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Video Dubbing (English to Arabic)", layout="centered")
st.title("Video Dubbing: English to Arabic")
st.write("Upload an English video or paste a YouTube URL, and get a dubbed Arabic version!")

# API Key
fanar_api_key = os.getenv("FANAR_API_KEY")
if not fanar_api_key:
    st.error("FANAR_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

client = FanarAPIClient(fanar_api_key)

st.subheader("Step 1: Choose Video Input")
input_video_path = None

# YouTube URL input
youtube_url = st.text_input("Paste a YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")

# File upload
video_file = st.file_uploader("Or upload your English video (mp4)", type=["mp4"])

# Handle input selection
if youtube_url and video_file:
    st.warning("Both YouTube URL and file upload detected. YouTube URL will take precedence.")
    video_file = None

if youtube_url:
    if st.button("Download from YouTube"):
        with st.spinner("Downloading video from YouTube..."):
            try:
                input_video_path = download_youtube_video(youtube_url)
                st.success(f"YouTube video downloaded successfully!")
                st.info(f"Video saved as: {input_video_path}")
            except Exception as e:
                st.error(f"Download failed: {str(e)}")
                st.stop()
elif video_file:
    input_video_path = "uploaded_video.mp4"
    with open(input_video_path, "wb") as f:
        f.write(video_file.read())
    st.success("Video uploaded successfully!")

# Process the video if we have one
if input_video_path and os.path.exists(input_video_path):
    st.success("✅ Video ready for processing!")
    
    # Extract video title for final filename
    video_title = get_video_title(input_video_path, youtube_url)
    sanitized_title = sanitize_filename(video_title)
    final_video_filename = f"{sanitized_title} - arabic dub.mp4"
    
    # Show video info
    file_size = os.path.getsize(input_video_path) / (1024 * 1024)  # MB
    st.info(f"📁 Video file: {input_video_path} ({file_size:.2f} MB)")
    st.info(f"🎬 Video title: {video_title}")
    st.info(f"📝 Final output will be: {final_video_filename}")
    
    # Optional: Show video preview
    if st.checkbox("Show video preview"):
        st.video(input_video_path)
    
    st.subheader("Step 2: Processing Pipeline")
    
    # User preferences
    st.write("**Processing Options:**")
    auto_cleanup = st.checkbox("🧹 Enable automatic cleanup of temporary files", value=True, 
                              help="Automatically remove temporary files after processing is complete")
    
    # File paths
    audio_file = "english_audio.wav"
    transcription_file = "transcription.txt"
    translation_file = "translation.txt"
    tts_output_file = "arabic_speech.wav"
    audioless_video_file = "audioless_video.mp4"
    output_file = final_video_filename

    # Step 1: Extract audio
    with st.spinner("Extracting audio from video..."):
        try:
            extract_audio_from_video(input_video_path, audio_file)
            st.success("Audio extracted!")
        except Exception as e:
            st.error(f"Audio extraction failed: {e}")
            st.stop()

    # Step 1.5: Separate music from English audio using Demucs
    with st.spinner("Separating music from English audio..."):
        try:
            music_path = separate_music_with_demucs(audio_file)
            st.success("Music separated from English audio!")
        except Exception as e:
            st.error(f"Music separation failed: {e}")
            st.stop()

    # Step 2: Transcribe audio
    with st.spinner("Transcribing audio to text..."):
        try:
            # Determine audio duration and select appropriate model
            audio_duration = get_audio_duration(audio_file)
            auto_selected_model = select_transcription_model(audio_duration)
            
            if audio_duration:
                st.info(f"Audio duration: {audio_duration:.1f} seconds")
            
            # Allow user to override model selection
            st.subheader("Transcription Model Selection")
            st.write("**Available Models:**")
            st.write("- **Fanar-Aura-STT-1**: Optimized for short audio clips (up to 20-30 seconds)")
            st.write("- **Fanar-Aura-STT-LF-1**: Optimized for long-form transcription of longer audio files")
            
            model_options = ["Auto-select (Recommended)", "Fanar-Aura-STT-1", "Fanar-Aura-STT-LF-1"]
            selected_model_option = st.selectbox(
                "Choose transcription model:",
                model_options,
                index=0
            )
            
            if selected_model_option == "Auto-select (Recommended)":
                selected_model = auto_selected_model
                st.info(f"Auto-selected model: {selected_model}")
            else:
                selected_model = selected_model_option
                st.info(f"Manually selected model: {selected_model}")
            
            transcription_result = client.transcribe_audio_fanar(audio_file, model=selected_model)
            transcription_text = transcription_result.get("text", "")
            if not transcription_text:
                transcription_text = str(transcription_result)
            save_text_to_file(transcription_text, transcription_file)
            st.success("Transcription complete!")
            st.text_area("Transcription (English)", transcription_text, height=150)
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            st.stop()

    # Step 3: Add grammar to transcription
    with st.spinner("Improving transcription grammar..."):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Add grammar to the following transcription:\n\n{transcription_text}"}
            ]
            grammar_result = client.fanar_chat(messages, model="Fanar")
            grammar_text = grammar_result.get("reply", "")
            if not grammar_text:
                grammar_text = transcription_text
            save_text_to_file(grammar_text, transcription_file)
            st.success("Grammar improved!")
            st.text_area("Grammar-Enhanced Transcription", grammar_text, height=150)
        except Exception as e:
            st.error(f"Grammar improvement failed: {e}")
            st.stop()

    # Step 4: Translate to Arabic
    with st.spinner("Translating to Arabic..."):
        try:
            translated_text = client.translate_text(grammar_text)
            save_text_to_file(translated_text, translation_file)
            st.success("Translation complete!")
            st.text_area("Translation (Arabic)", translated_text, height=150)
        except Exception as e:
            st.error(f"Translation failed: {e}")
            st.stop()

    # Step 5: Improve Arabic for TTS
    with st.spinner("Improving Arabic for TTS..."):
        try:
            messages = [
                {"role": "system", "content": "أنت مساعد لغوي مختص بتحسين النصوص لتحويلها إلى كلام (TTS) بطريقة طبيعية وسلسة."},
                {"role": "user", "content": f"""قم بإعادة صياغة هذا النص ليكون أكثر سلاسة وطبيعية عند النطق لتحسين أداء تحويل النص إلى كلام (TTS)، ويجب أن يكون النص الناتج أكثر إيجازًا واختصارًا من النص الأصلي، مع الحفاظ على المعنى الأساسي. استخدم جملاً قصيرة، وتجنّب التعقيد أو الكلمات الزائدة. لا تضف مقدمات أو تعليقات أو اقتباسات — فقط أرجع النص المحسّن النهائي.\n\nالنص:\n{translated_text}"""}
            ]
            grammar_result = client.fanar_chat(messages, model="Fanar")
            grammar_text = grammar_result.get("reply", "")
            if not grammar_text:
                grammar_text = translated_text
            save_text_to_file(grammar_text, translation_file)
            st.success("Arabic improved for TTS!")
            st.text_area("TTS-Optimized Arabic", grammar_text, height=150)
        except Exception as e:
            st.error(f"Arabic TTS improvement failed: {e}")
            st.stop()

    # Step 5.5: Extract only quoted text for TTS
    quoted_texts = re.findall(r'"([^"]+)"|"([^"]+)"|«([^»]+)»', grammar_text)
    # Flatten and join all non-empty matches
    speech_text = ' '.join([t for group in quoted_texts for t in group if t])
    if not speech_text:
        st.warning("No text found in quotation marks. TTS will be skipped.")
    else:
        st.text_area("Text to be used for TTS (from quotes only)", speech_text, height=100)

    # Step 6: Text-to-Speech
    if speech_text:
        with st.spinner("Converting quoted Arabic text to speech..."):
            try:
                output_audio = client.text_to_speech(speech_text, tts_output_file)
                st.success("TTS complete!")
                audio_file_display = open(tts_output_file, 'rb')
                st.audio(audio_file_display.read(), format='audio/wav')
            except Exception as e:
                st.error(f"TTS failed: {e}")
                st.stop()
    else:
        output_audio = None

    # Step 6.5: Match TTS audio duration to original audio
    if output_audio:
        try:
            # Load original and TTS audio
            original_audio = AudioSegment.from_file(audio_file)
            tts_audio = AudioSegment.from_file(tts_output_file)
            target_duration = len(original_audio)  # in milliseconds
            tts_duration = len(tts_audio)

            if tts_duration < target_duration:
                # Pad with silence at the end
                silence = AudioSegment.silent(duration=target_duration - tts_duration)
                adjusted_audio = tts_audio + silence
            else:
                # Trim to target duration
                adjusted_audio = tts_audio[:target_duration]

            # Save adjusted audio
            adjusted_audio.export(tts_output_file, format="wav")
            st.info(f"TTS audio adjusted to {target_duration/1000:.2f} seconds to match original audio.")
        except Exception as e:
            st.error(f"Audio duration adjustment failed: {e}")
            st.stop()

    # Step 6.6: Mix separated music with Arabic TTS audio
    if output_audio and music_path:
        try:
            mixed_tts_music_path = "arabic_speech_with_music.wav"
            mix_music_and_tts(music_path, tts_output_file, mixed_tts_music_path)
            tts_output_file = mixed_tts_music_path  # Use mixed audio for final video
            st.success("Music mixed with Arabic TTS audio!")
        except Exception as e:
            st.error(f"Mixing music with TTS audio failed: {e}")
            st.stop()

    # Step 7: Combine audio and video
    if output_audio:
        with st.spinner("Combining dubbed audio with video..."):
            try:
                combine_audio_video(tts_output_file, "audioless_video.mp4", output_file)
                st.success("Dubbed video created!")
                with open(output_file, "rb") as f:
                    st.download_button("Download Dubbed Video", f, file_name=final_video_filename)
                
                # Automatic cleanup of temporary files
                if auto_cleanup:
                    st.subheader("🧹 Cleanup")
                    temp_files = [
                        audio_file,
                        transcription_file,
                        translation_file,
                        tts_output_file,
                        audioless_video_file,
                        "arabic_speech_with_music.wav"
                    ]
                    
                    # Add music path if it exists
                    if 'music_path' in locals() and music_path and os.path.exists(music_path):
                        temp_files.append(music_path)
                    
                    # Clean up temporary files
                    cleaned_files = cleanup_temp_files(temp_files, keep_final_video=True)
                    cleanup_demucs_output()
                    
                    st.success("✅ Processing complete! Temporary files have been cleaned up.")
                else:
                    st.success("✅ Processing complete! Temporary files have been preserved.")
                    st.info("💡 You can run the cleanup script later: `python cleanup.py`")
                
            except Exception as e:
                st.error(f"Combining audio and video failed: {e}")
                st.stop()