import os
import groq
from dotenv import load_dotenv

class ContextExpander:
    def __init__(self):
        """ Initialize the Groq LLM client """
        # Load from .env file
        load_dotenv()
        
        # Try to get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        
        # If not found, prompt user for API key
        if not api_key:
            print("\nGROQ_API_KEY not found. Please enter your Groq API key:")
            api_key = input().strip()
            
            # Save to .env file for future use
            with open('.env', 'w') as f:
                f.write(f"GROQ_API_KEY={api_key}")
            
            # Set for current session
            os.environ["GROQ_API_KEY"] = api_key
        
        self.client = groq.Client(api_key=api_key)

    def expand_caption(self, caption):
        """ Expand the given caption using an LLM """
        try:
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a multilingual assistant. You MUST respond ONLY in the language specified in the user's prompt. Never mix languages or provide translations."},
                    {"role": "user", "content": caption}
                ],
                temperature=0.7,
                max_tokens=150  # Limit response length for more focused answers
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in expanding caption: {e}")
            return caption