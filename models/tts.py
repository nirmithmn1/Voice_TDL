from gtts import gTTS
import os
from gtts.lang import tts_langs

class TextToSpeech:
    def __init__(self):
        """Initialize the TTS engine"""
        self.available_languages = tts_langs()
        self.current_lang = 'en'
        # Set TLD based on language for better accent
        self.tld_map = {
            'en': 'com',
            'hi': 'co.in',
            'kn': 'co.in',
            'te': 'co.in',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'ja': 'co.jp'
        }
        self.tld = self.tld_map['en']
        
    def set_language(self, lang='en'):
        """Change language and corresponding TLD"""
        self.current_lang = lang
        self.tld = self.tld_map.get(lang, 'com')

    def get_language_name(self, lang_code):
        """Get full language name from code"""
        return self.available_languages.get(lang_code, "Unknown")
        
    def set_language(self, lang='en'):
        """Change language"""
        self.current_lang = lang

    def generate_speech(self, text, output_path="outputs/speech_output.wav"):
        """Convert text into speech and save it as a WAV file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            tts = gTTS(text=text, lang=self.current_lang, tld=self.tld)
            tts.save(output_path)
        except Exception as e:
            print(f"Error generating speech: {e}")
