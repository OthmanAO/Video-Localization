import streamlit as st
import os
from en_audio_to_ar_audio import FanarAPIClient, extract_audio_from_video, save_text_to_file, load_text_from_file, combine_audio_video
from dotenv import load_dotenv
import re
from pydub import AudioSegment
import subprocess
import glob

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

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Video Dubbing (English to Arabic)", layout="centered")
st.title("🎬 Video Dubbing: English to Arabic")
st.write("Upload an English video, and get a dubbed Arabic version!")

# API Key
fanar_api_key = os.getenv("FANAR_API_KEY")
if not fanar_api_key:
    st.error("FANAR_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

client = FanarAPIClient(fanar_api_key)

# File upload
video_file = st.file_uploader("Upload your English video (mp4)", type=["mp4"])

if video_file:
    # Save uploaded file
    input_video_path = "uploaded_video.mp4"
    with open(input_video_path, "wb") as f:
        f.write(video_file.read())
    st.success("Video uploaded!")

    # File paths
    audio_file = "english_audio.wav"
    transcription_file = "transcription.txt"
    translation_file = "translation.txt"
    tts_output_file = "arabic_speech.wav"
    audioless_video_file = "audioless_video.mp4"
    output_file = "final_video.mp4"

    # Step 1: Extract audio
    with st.spinner("Extracting audio from video..."):
        try:
            extract_audio_from_video(input_video_path, audio_file)
            st.success("Audio extracted!")
        except Exception as e:
            st.error(f"Audio extraction failed: {e}")
            st.stop()

    # Step 1.5: Separate music from English audio using Demucs
    with st.spinner("Separating music from English audio (Demucs)..."):
        try:
            music_path = separate_music_with_demucs(audio_file)
            st.success("Music separated from English audio!")
        except Exception as e:
            st.error(f"Music separation failed: {e}")
            st.stop()

    # Step 2: Transcribe audio
    with st.spinner("Transcribing audio to text..."):
        try:
            transcription_result = client.transcribe_audio_fanar(audio_file, model="Fanar-Aura-STT-1")
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
                    st.download_button("Download Dubbed Video", f, file_name="dubbed_arabic_video.mp4")
            except Exception as e:
                st.error(f"Combining audio and video failed: {e}")
                st.stop() 