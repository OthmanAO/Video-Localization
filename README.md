# Fanar Video Localization Pipeline 🎥🗣️🌍

This project provides a complete pipeline for **localizing English videos into Arabic**, using the [Fanar API](https://fanar.qa). It performs:

1. **Audio extraction** from video  
2. **Speech-to-text** transcription  
3. **Grammar correction** via LLM  
4. **Text translation** to Arabic  
5. **Natural Arabic reformulation** for TTS  
6. **Text-to-speech synthesis**  
7. **Recombination of audio and video**

---

## 🚀 Features

- Extracts audio from any video file
- Transcribes speech using Fanar STT model
- Enhances and grammatically corrects transcripts using Fanar Chat
- Translates English to Arabic using Fanar MT
- Prepares Arabic text for smooth TTS rendering
- Generates natural-sounding Arabic audio using Fanar TTS
- Merges audio with the original video (with removed audio)

---

## 🛠️ Requirements

Install the dependencies with:

```bash
pip install -r requirements.txt

Required Python packages:
	•	requests
	•	moviepy
	•	python-dotenv

Also ensure ffmpeg is installed and available in your system path:

# Ubuntu / Debian
sudo apt install ffmpeg

# MacOS (with Homebrew)
brew install ffmpeg


⸻

📁 Setup
	1.	Clone the repository

git clone https://github.com/yourusername/fanar-video-localizer.git
cd fanar-video-localizer

	2.	Add your Fanar API key

Create a .env file in the root directory:

FANAR_API_KEY=your_fanar_api_key_here

	3.	Place your input video

Put the English video in the root directory and name it:

english_video1.mp4


⸻

▶️ Usage

Run the full pipeline:

python main.py

This will:
	•	Extract audio to english_audio.wav
	•	Generate transcript in transcription.txt
	•	Save Arabic translation in translation.txt
	•	Output TTS audio to arabic_speech.wav
	•	Final combined video as final_video.mp4

⸻

🧠 How It Works
	•	FanarAPIClient wraps all Fanar endpoints:
	•	chat/completions for grammar and TTS refinement
	•	audio/transcriptions for STT
	•	translations for English-Arabic
	•	audio/speech for TTS
	•	Video/audio utils extract and reattach audio
	•	main() orchestrates the full localization process

⸻

📂 Output Files

File	Description
english_audio.wav	Extracted audio
transcription.txt	Transcribed and cleaned text
translation.txt	Translated Arabic text
arabic_speech.wav	TTS Arabic audio
audioless_video.mp4	Original video with audio removed
final_video.mp4	Final Arabic-localized video


⸻

📝 Notes
	•	For longer videos, ensure your Fanar account allows for larger STT/TTS jobs.
	•	Translations and grammar fixes use Fanar Chat LLM — adjust prompts as needed.

⸻

📜 License

MIT License. See LICENSE file for details.

⸻

🙏 Acknowledgments

Built using the Fanar API for voice, language, and LLM tasks.

---

Let me know if you want badges, logo support, or a GIF preview of the final output video!
