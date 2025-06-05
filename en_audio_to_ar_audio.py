import requests
import os
from moviepy import VideoFileClip, AudioFileClip
from dotenv import load_dotenv
import subprocess




class FanarAPIClient:
    """Client for interacting with Fanar API services."""
    
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = "https://api.fanar.qa/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        
        
    
    def fanar_chat(self, messages, model="Fanar", max_tokens=1000):
        """"
        Send a chat message to the Fanar API and get a response.
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            model (str): Model to use for chat
            max_tokens (int): Maximum number of tokens in the response
        Returns:
            dict: API-like response with chat reply
        """
        
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": model,
            "messages": messages
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if 'choices' not in result or len(result['choices']) == 0:
                raise Exception("No choices found in response")
                
            reply = result['choices'][0]['message']['content']
            return {"reply": reply}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Chat API request failed: {e}")
        except Exception as e:
            raise Exception(f"Error processing chat response: {e}")
        
    

    
    def transcribe_audio_fanar(self, file_path, model="Fanar-Aura-STT-LF-1"):
        """
        Transcribe audio file to text.
        
        Args:
            file_path (str): Path to audio file
            model (str): STT model to use
            
        Returns:
            dict: API response with transcription
        """
        url = f"{self.base_url}/audio/transcriptions"
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise Exception(f"Audio file not found: {file_path}")
            
            # Get file size to help choose the right model
            file_size = os.path.getsize(file_path)
            print(f"Audio file size: {file_size} bytes")
            
            # Detect file type from extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Set appropriate MIME type
            mime_types = {
                '.wav': 'audio/wav',
                '.mp3': 'audio/mpeg',
                '.m4a': 'audio/m4a',
                '.flac': 'audio/flac',
                '.ogg': 'audio/ogg',
                '.webm': 'audio/webm'
            }
            
            mime_type = mime_types.get(file_ext, 'audio/wav')
            
            with open(file_path, 'rb') as audio_file:
                files = {
                    'file': (os.path.basename(file_path), audio_file, mime_type)
                }
                
                data = {
                    'model': model
                }
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=300 
                )
                
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    print(f"Error response content: {response.text}")
                
                response.raise_for_status()
                return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("Request timed out - the audio file might be too large or the server is slow")
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"Transcription API request failed: {e}"
                if e.response.status_code == 500:
                    error_msg += "\nInternal server error - this might be due to:"
                    error_msg += "\n- Audio file format not supported"
                    error_msg += "\n- Audio file too large or corrupted"
                    error_msg += "\n- Wrong model selected for file duration"
                    error_msg += "\n- API service temporarily unavailable"
                elif e.response.status_code == 401:
                    error_msg += "\nUnauthorized - check your API key"
                elif e.response.status_code == 403:
                    error_msg += "\nForbidden - you may need additional authorization for this endpoint"
                try:
                    error_details = e.response.json()
                    error_msg += f"\nAPI Error Details: {error_details}"
                except:
                    error_msg += f"\nResponse text: {e.response.text}"
                raise Exception(error_msg)
            else:
                raise Exception(f"Network error: {e}")
        except Exception as e:
            raise Exception(f"Error processing audio file: {e}")
    
    def seperate_music_from_audio(self, audio_file, output_file):
        """
        Separate music from audio file using Spleeter or similar tool.
        
        Args:
            audio_file (str): Path to input audio file
            output_file (str): Path for output audio file without music
            
        Returns:
            str: Path to output audio file
        """
        # This function is a placeholder for music separation logic.
        # TODO: Implement music seperation using a library like Spleeter or a custom model.
        raise NotImplementedError("Music separation is not implemented in this example.")
    
    
    def translate_text(self, text, source_lang="en", target_lang="ar", model="Fanar-Shaheen-MT-1"):
        """
        Translate text between languages.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code
            target_lang (str): Target language code
            model (str): Translation model to use
            
        Returns:
            str: Translated text
        """
        url = f"{self.base_url}/translations"
        
        data = {
            "model": model,
            "text": text,
            "langpair": f"{source_lang}-{target_lang}",
            "preprocessing": "default"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            translated_text = result.get("text")
            if not translated_text:
                raise Exception("No translated text found in response")
                
            return translated_text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Translation API request failed: {e}")
    
    def text_to_speech(self, text, output_file="output_speech.wav", model="Fanar-Aura-TTS-1", voice="default"):
        """
        Convert text to speech and save as audio file.
        
        Args:
            text (str): Text to convert
            output_file (str): Output audio file path
            model (str): TTS model to use
            voice (str): Voice to use
            
        Returns:
            str: Path to saved audio file
        """
        url = f"{self.base_url}/audio/speech"
        
        payload = {
            "model": model,
            "input": text,
            "voice": voice
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            with open(output_file, "wb") as f:
                f.write(response.content)
                
            return os.path.abspath(output_file)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"TTS API request failed: {e}")


def extract_audio_from_video(video_path, audio_path):
    """
    Extract audio from video file.
    
    Args:
        video_path (str): Path to input video file
        audio_path (str): Path for extracted audio file
    """
    try:
        with VideoFileClip(video_path) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path)
            
            new_clip = video_clip.without_audio()
            new_clip.write_videofile("audioless_video.mp4")
            
        
        print(f"Audio extracted and saved to {audio_path}")
        
    except Exception as e:
        raise Exception(f"Audio extraction failed: {e}")


def save_text_to_file(text, file_path):
    """Save text to file with UTF-8 encoding."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text saved to {file_path}")
    except Exception as e:
        raise Exception(f"Error saving text to file: {e}")


def load_text_from_file(file_path):
    """Load text from file with UTF-8 encoding."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading text from file: {e}")


def combine_audio_video(audio_file, video_file, output_file):
    """Combine audio and video files into a single output file using FFMPEG directly."""
    
    try:
        print("Starting audio-video combination...")
        # FFMPEG command to combine audio and video
        command = [
            'ffmpeg',
            '-i', video_file,  
            '-i', audio_file,  
            '-c:v', 'copy',    
            '-c:a', 'aac',     
            '-b:a', '192k',    
            '-strict', 'experimental',
            '-map', '0:v',     
            '-map', '1:a',     
            '-shortest',       
            '-y',              
            output_file
        ]
        
        # Run FFMPEG command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for process to complete
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFMPEG error: {stderr.decode()}")
            
        print(f"Successfully combined audio and video into {output_file}")
        
    except Exception as e:
        raise Exception(f"Error combining audio and video: {e}")




def main():
    """Main processing pipeline: video -> audio -> transcription -> translation -> TTS"""
    
    # Load environment variables
    load_dotenv()
    fanar_api_key = os.getenv("FANAR_API_KEY")
    
    if not fanar_api_key:
        print("Error: FANAR_API_KEY not found in environment variables")
        return
    
    # Initialize API client
    try:
        client = FanarAPIClient(fanar_api_key)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # File paths
    video_file = "english_video1.mp4"
    audio_file = "english_audio.wav"  
    transcription_file = "transcription.txt"
    translation_file = "translation.txt"
    tts_output_file = "arabic_speech.wav"
    audioless_video_file = "audioless_video.mp4"
    output_file = "final_video.mp4"
    
    
   
    try:
        # Step 1: Check if video file exists
        if not os.path.exists(video_file):
            print(f"Error: Video file '{video_file}' not found")
            return
        
        # Step 2: Seperate audio from video
        print(f"Seperate audio from {video_file}...")
        extract_audio_from_video(video_file, audio_file)
        
        if not os.path.exists(audio_file):
            print(f"Error: Audio file '{audio_file}' was not created")
            return
        
        # Step 3: Seperate music from audio
        print("Seperate music from audio...")
        # Note: This step is not implemented in this example, but you can use a library like Spleeter or a custom model for this.
        
        
        # Step 4: Transcribe audio to text using Fanar API
        print("Transcribing audio to text...")
        transcription_result = client.transcribe_audio_fanar(audio_file, model="Fanar-Aura-STT-1")
        
        # Extract text from response
        transcription_text = transcription_result.get("text", "")
        if not transcription_text:
            transcription_text = str(transcription_result)
        
        # Save transcription text to file    
        save_text_to_file(transcription_text, transcription_file)
        print("Transcription completed successfully!")
        
        # Step 5: Add grammar to transcription
        print("Adding grammar to transcription...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Add grammar to the following transcription:\n\n{transcription_text}"}
        ]
        grammar_result = client.fanar_chat(messages, model="Fanar")
        grammar_text = grammar_result.get("reply", "")    
        if not grammar_text:
            grammar_text = transcription_text
        save_text_to_file(grammar_text, transcription_file)
        print("Grammar added successfully!")
                
        # Step 6: Translate text to Arabic
        print("Translating text to Arabic...")
        translated_text = client.translate_text(transcription_text)
        save_text_to_file(translated_text, translation_file)
        print("Translation completed successfully!")
        
        # Step 7: Process translation for better TTS performance
        print("Adding grammar to translation...")
        messages = [
            {"role": "system", "content": "أنت مساعد لغوي مختص بتحسين النصوص لتحويلها إلى كلام (TTS) بطريقة طبيعية وسلسة."},
            {"role": "user", "content": f"""قم بإعادة صياغة هذا النص ليكون أكثر سلاسة وطبيعية عند النطق لتحسين أداء تحويل النص إلى كلام (TTS)، ولكن يجب ألا يكون أطول من النص الأصلي. استخدم جملاً قصيرة، وتجنّب التعقيد أو الكلمات الزائدة. لا تضف مقدمات أو تعليقات أو اقتباسات — فقط أرجع النص المحسّن النهائي.\n\nالنص:\n{translated_text}"""}
        ]
        grammar_result = client.fanar_chat(messages, model="Fanar")
        grammar_text = grammar_result.get("reply", "")    
        if not grammar_text:
            grammar_text = translated_text
        save_text_to_file(grammar_text, translation_file)
        print("Grammar added successfully!")
        
        translated_text = load_text_from_file(translation_file)
        
        # Step 8: Convert translated text to speech
        print("Converting translated text to speech...")
        output_audio = client.text_to_speech(translated_text, tts_output_file)
        print(f"Text-to-speech conversion completed! Audio saved to {output_audio}")
        
        # Step 9: Combine audio and video
        print("Combining audio and video...")
        combine_audio_video(tts_output_file, audioless_video_file, output_file)  
        print("Audio and video combined successfully!")
        
        print("\n" + "="*50)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Original video: {os.path.abspath(video_file)}")
        print(f"Extracted audio: {os.path.abspath(audio_file)}")
        print(f"Transcription: {os.path.abspath(transcription_file)}")
        print(f"Grammar added transcription: {os.path.abspath(transcription_file)}")
        print(f"Translation: {os.path.abspath(translation_file)}")
        print(f"Grammar added translation: {os.path.abspath(translation_file)}")
        print(f"Arabic speech: {os.path.abspath(tts_output_file)}")
        print(f"Combined video with audio: {os.path.abspath(output_file)}")
        
        
        
    except Exception as e:
        print(f"Error in processing pipeline: {e}")


if __name__ == "__main__":
    main()