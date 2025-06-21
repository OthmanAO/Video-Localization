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
        """
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