import os
import speech_recognition as sr
from models.blip2 import ImageCaptioning
from models.tts import TextToSpeech
from utils.file_utils import save_text
from models.context_expander import ContextExpander

# Define paths
IMAGE_PATH = "data/hall.jpg"
CAPTION_PATH = "outputs/caption.txt"
AUDIO_OUTPUT_PATH = "outputs/speech_output.wav"
AUDIO_INPUT_PATH = "outputs/question.wav"

def get_audio_question():
    """Get question from user through microphone"""
    recognizer = sr.Recognizer()
    
    print("\nPlease ask your question about the image (speak clearly)...")
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Processing your question...")
            question = recognizer.recognize_google(audio)
            print(f"You asked: {question}")
            return question
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

def main():
    # Step 1: Generate Caption from Image
    print("Generating caption for image...")
    captioning_model = ImageCaptioning()
    caption = captioning_model.generate_caption(IMAGE_PATH)
    print(f"Generated Caption: {caption}")

    # Initialize models
    expander = ContextExpander()
    tts_model = TextToSpeech()

    while True:
        # Get audio question from user
        print("\nPress Enter to ask a question, or type 'quit' to exit")
        user_input = input()
        
        if user_input.lower() == 'quit':
            break

        question = get_audio_question()
        
        if question is None:
            continue

        # Generate response using context expander
        prompt = f"Based on this image caption: '{caption}', please answer the following question: {question}"
        response = expander.expand_caption(prompt)
        print(f"\nResponse: {response}")

        # Convert response to speech
        print("Converting response to speech...")
        tts_model.generate_speech(response, AUDIO_OUTPUT_PATH)
        print(f"Speech output saved to: {AUDIO_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
