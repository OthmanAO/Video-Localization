# Fanar Video Localization Pipeline 🎥🗣️🌍

This project provides a complete pipeline for **localizing English videos into Arabic**, using the [Fanar API](https://fanar.qa). It performs:

1. **Audio extraction** from video
2. **Music/vocals separation** (Demucs)
3. **Speech-to-text** transcription (with smart model selection)
4. **Grammar improvement** of English transcript (LLM)
5. **Translation** to Arabic
6. **Arabic reformulation for TTS** (LLM, concise and natural)
7. **Extraction of quoted/target speech** for TTS
8. **Text-to-speech synthesis** (Arabic)
9. **Duration matching** (pad/trim TTS to match original)
10. **Music re-mixing** (combine separated music with Arabic TTS)
11. **Recombination of dubbed audio and video**

---

## 🚀 Features

- Download videos from YouTube or upload your own
- Extracts and separates music from any video file
- Transcribes speech using Fanar STT model (auto or manual model selection)
- Enhances and grammatically corrects transcripts using Fanar Chat
- Translates English to Arabic using Fanar MT
- Reformulates Arabic for smooth, natural TTS (shorter, simpler sentences)
- Extracts only quoted/target speech for dubbing
- Generates natural-sounding Arabic audio using Fanar TTS
- Matches TTS audio duration to original for lip sync
- Mixes separated music back with dubbed speech
- Merges audio with the original video (with removed audio)
- Automatic filename generation with original title + "arabic dub" suffix
- Automatic cleanup of temporary files (optional)

---

## 📁 Project Structure

```
FanarVideoLocalization/
├── dubbing_ui.py          # Main Streamlit application
├── dubbing_utils.py       # Core processing functions and API client
├── cleanup.py             # Cleanup script for temporary files
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

---

## 🔧 Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file in the project root and add your Fanar API key:
   ```
   FANAR_API_KEY=your_fanar_api_key_here
   ```
3. Run the app: `streamlit run dubbing_ui.py`

---

## 🧹 Cleanup

The project generates temporary files during processing. To clean up:

```bash
python cleanup.py
```

This removes:

- Temporary audio/video files
- Transcription and translation files
- Demucs output directories
- Python cache files

---

## 📝 Usage

1. Upload a video file or paste a YouTube URL
2. The app will automatically:
   - Extract audio and separate music/vocals
   - Transcribe speech and improve grammar
   - Translate and reformulate Arabic for TTS
   - Extract quoted/target speech for dubbing
   - Synthesize Arabic speech, match duration, and mix with music
   - Generate final video with Arabic dub
3. Download the final video with descriptive filename
