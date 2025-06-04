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
