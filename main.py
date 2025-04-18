import os
import speech_recognition as sr
from models.blip2 import ImageCaptioning
from models.tts import TextToSpeech
from utils.file_utils import save_text
from models.context_expander import ContextExpander
import subprocess

# Define paths
IMAGE_PATH = "data/mt.jpg"
CAPTION_PATH = "outputs/caption.txt"
AUDIO_OUTPUT_PATH = "outputs/speech_output.wav"
AUDIO_INPUT_PATH = "outputs/question.wav"

# Define common languages
COMMON_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'kn': 'Kannada',
    'te': 'Telugu',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'ja': 'Japanese'
}

def get_audio_question():
    """Get question from user through microphone"""
    recognizer = sr.Recognizer()
    
    print("\nPlease ask your question about the image (speak clearly)...")
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=12)
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

def play_audio(audio_path):
    """Play the generated audio file"""
    try:
        if os.path.exists(audio_path):
            subprocess.run(['afplay', audio_path], check=True)
        else:
            print(f"Audio file not found at: {audio_path}")
    except subprocess.CalledProcessError:
        print("Error playing audio file")

def select_language(tts_model, recognizer):
    """Let user select language through voice"""
    # First announcement in English
    intro_text = "Please select your preferred language. Available languages are: "
    for code, name in COMMON_LANGUAGES.items():
        intro_text += f"{name}, "
    intro_text += ". Please speak the language name."
    
    tts_model.generate_speech(intro_text)
    play_audio(AUDIO_OUTPUT_PATH)
    
    print("\nListening for language selection...")
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=8)
            language_choice = recognizer.recognize_google(audio).lower()
            
            # Fixed: Changed common_languages to COMMON_LANGUAGES
            lang_code_map = {name.lower(): code for code, name in COMMON_LANGUAGES.items()}
            selected_lang = lang_code_map.get(language_choice, 'en')
            
            # Confirm selection only in selected language
            confirm_texts = {
                'en': "Selected language: English. The system will now speak in English",
                'hi': "चयनित भाषा: हिंदी। सिस्टम अब हिंदी में बोलेगा",
                'kn': "ಆಯ್ಕೆ ಮಾಡಿದ ಭಾಷೆ: ಕನ್ನಡ. ಸಿಸ್ಟಮ್ ಈಗ ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡುತ್ತದೆ",
                'te': "ఎంచుకున్న భాష: తెలుగు. సిಸ్ಟమ్ ఇప్పుడు తెలుగులో మాట్లాడుతుంది",
                'es': "Idioma seleccionado: Español. El sistema ahora hablará en español",
                'fr': "Langue sélectionnée : Français. Le système parlera maintenant en français",
                'de': "Ausgewählte Sprache: Deutsch. Das System wird jetzt auf Deutsch sprechen",
                'ja': "選択された言語：日本語。システムは日本語で話します"
            }
            
            # Directly confirm in selected language
            tts_model.set_language(selected_lang)
            tts_model.generate_speech(confirm_texts[selected_lang])
            play_audio(AUDIO_OUTPUT_PATH)
            
            return selected_lang
            
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            tts_model.generate_speech("Could not understand. Using English as default.")
            play_audio(AUDIO_OUTPUT_PATH)
            return 'en'

def main():
    # Step 1: Generate Caption from Image
    print("Generating caption for image...")
    captioning_model = ImageCaptioning()
    caption = captioning_model.generate_caption(IMAGE_PATH)
    print(f"Generated Caption: {caption}")

    # Initialize models
    expander = ContextExpander()
    tts_model = TextToSpeech()
    recognizer = sr.Recognizer()
    
    # Select language through voice
    selected_lang = select_language(tts_model, recognizer)

    # Welcome messages in different languages
    welcome_messages = {
        'en': "Please press Enter to ask your question about the image, or say quit to exit",
        'hi': "छवि के बारे में अपना प्रश्न पूछने के लिए एंटर दबाएं, या बाहर निकलने के लिए quit कहें",
        'kn': "ಚಿತ್ರದ ಬಗ್ಗೆ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಲು ಎಂಟರ್ ಒತ್ತಿ, ಅಥವಾ ನಿರ್ಗಮಿಸಲು quit ಎಂದು ಹೇಳಿ",
        'te': "చిత్రం గురించి మీ ప్రశ్నను అడగడానికి ఎంటర్ నొక్కండి, లేదా నిష్క్రమించడానికి quit అని చెప్పండి",
        'es': "Presione Enter para hacer su pregunta sobre la imagen, o diga salir para terminar",
        'fr': "Appuyez sur Entrée pour poser votre question sur l'image, ou dites quitter pour sortir",
        'de': "Drücken Sie Enter, um Ihre Frage zum Bild zu stellen, oder sagen Sie beenden zum Verlassen",
        'ja': "画像について質問するにはEnterを押すか、終了するにはquitと言ってください"
    }

    # Show welcome message once
    tts_model.generate_speech(welcome_messages[selected_lang])
    play_audio(AUDIO_OUTPUT_PATH)

    while True:
        user_input = input()
        if user_input.lower() == 'quit':
            break

        question = get_audio_question()
        if question is None:
            continue

        # Generate response using context expander
        language_prompts = {
            'en': f"Answer this specific question about the image: '{question}' based on this caption: '{caption}'. Respond ONLY in English. Be direct and brief.",
            'hi': f"इस छवि के बारे में यह प्रश्न: '{question}' इस विवरण के आधार पर: '{caption}'. केवल हिंदी में एक संक्षिप्त उत्तर दें।",
            'kn': f"ಈ ಚಿತ್ರದ ಬಗ್ಗೆ ಈ ಪ್ರಶ್ನೆ: '{question}' ಈ ವಿವರಣೆಯ ಆಧಾರದಲ್ಲಿ: '{caption}'. ಕೇವಲ ಕನ್ನಡದಲ್ಲಿ ಸಂಕ್ಷಿಪ್ತ ಉತ್ತರ ನೀಡಿ.",
            'te': f"ఈ చిత్రంపై ప్రశ్న: '{question}' ఈ వివరణ ఆధారంగా: '{caption}'. తెలుగులో మాత్రమే సంಕ్ಷిप్त సమాధానం ఇవ్వండి.",
            'es': f"Responde esta pregunta sobre la imagen: '{question}' basado en esta descripción: '{caption}'. Responde SOLO en español. Sé breve.",
            'fr': f"Réponds à cette question sur l'image: '{question}' basé sur cette description: '{caption}'. Réponds UNIQUEMENT en français. Sois bref.",
            'de': f"Beantworte diese Frage zum Bild: '{question}' basierend auf dieser Beschreibung: '{caption}'. Antworte NUR auf Deutsch. Sei kurz.",
            'ja': f"この画像についての質問: '{question}' この説明に基づいて: '{caption}'. 日本語のみで簡潔に答えてください。"
        }
        
        prompt = language_prompts.get(selected_lang, language_prompts['en'])
        # Force LLM to respond in selected language
        prompt += f"\n\nIMPORTANT: You must respond ONLY in {COMMON_LANGUAGES[selected_lang]}. Do not translate or provide responses in any other language."
        response = expander.expand_caption(prompt)
        print(f"\nResponse: {response}")

        # Convert response to speech in selected language
        print("Converting response to speech...")
        tts_model.generate_speech(response, AUDIO_OUTPUT_PATH)
        print(f"Speech output saved to: {AUDIO_OUTPUT_PATH}")
        
        print("Playing audio response...")
        play_audio(AUDIO_OUTPUT_PATH)

if __name__ == "__main__":
    main()
