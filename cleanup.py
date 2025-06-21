#!/usr/bin/env python3
"""
Cleanup script for the QCRI2025 video dubbing project.
Removes temporary files generated during video processing.
"""

import os
import glob

def cleanup_temp_files():
    """Remove temporary files generated during video processing."""
    
    # Files to remove
    temp_files = [
        "final_video.mp4",
        "arabic_speech_with_music.wav",
        "arabic_speech.wav",
        "transcription.txt",
        "translation.txt",
        "audioless_video.mp4",
        "english_audio.wav",
        "downloaded_youtube_video.mp4",
        "uploaded_video.mp4",
        "english_audio1.wav",
        "english_video1.mp4",
        "test_audio.wav",
        ".DS_Store"
    ]
    
    # Directories to remove
    temp_dirs = [
        "__pycache__",
        "demucs_output"
    ]
    
    # Remove files
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Removed: {file}")
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    # Remove directories
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            try:
                import shutil
                shutil.rmtree(dir_name)
                print(f"✅ Removed directory: {dir_name}")
            except Exception as e:
                print(f"❌ Failed to remove directory {dir_name}: {e}")
    
    # Remove any remaining .mp4, .wav files (except audio_example.mp3)
    for pattern in ["*.mp4", "*.wav"]:
        for file in glob.glob(pattern):
            if file != "audio_example.mp3":  # Keep the example file
                try:
                    os.remove(file)
                    print(f"✅ Removed: {file}")
                except Exception as e:
                    print(f"❌ Failed to remove {file}: {e}")
    
    print("\n🎉 Cleanup completed!")

if __name__ == "__main__":
    print("🧹 Starting cleanup of temporary files...")
    cleanup_temp_files() 