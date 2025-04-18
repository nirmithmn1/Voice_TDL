import pyttsx3
import os

class TextToSpeech:
    def __init__(self):
        """Initialize the pyttsx3 engine"""
        self.engine = pyttsx3.init()
        # Configure properties (optional)
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

    def generate_speech(self, text, output_path="outputs/speech_output.wav"):
        """Convert text into speech and save it as a WAV file"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Generate and save the audio
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error generating speech: {e}")