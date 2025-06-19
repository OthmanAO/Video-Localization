from en_audio_to_ar_audio import FanarAPIClient, extract_audio_from_video, combine_audio_video
import os

def test_audio_processing():
    # Input files
    video_file = "english_video1.mp4"
    audio_file = "english_audio.wav"
    music_only_audio = "test_audio.wav"
    
    try:
        # Step 1: Extract audio from video
        print("Extracting audio from video...")
        extract_audio_from_video(video_file, audio_file)
        
        # Step 2: Extract only the music track
        print("Extracting music track...")
        client = FanarAPIClient("dummy_key") 
        client.extract_music_from_audio(audio_file, music_only_audio)
        
        print("\nTest completed successfully!")
        print(f"Original video: {os.path.abspath(video_file)}")
        print(f"Original audio: {os.path.abspath(audio_file)}")
        print(f"Music-only audio: {os.path.abspath(music_only_audio)}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_audio_processing() 