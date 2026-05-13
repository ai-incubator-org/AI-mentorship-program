import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load environment variables (like your OPENAI_API_KEY) from the .env file
load_dotenv()

# 2. Initialize the OpenAI client
# It automatically looks for an environment variable named OPENAI_API_KEY
client = OpenAI()

def translate_text(text: str, target_language: str) -> str:
    """
    Translates text to the target language using OpenAI's GPT model.
    """
    try:
        # 3. Call the OpenAI API using the chat completions endpoint
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can also use "gpt-4o" or other chat models
            messages=[
                # The system prompt sets the behavior of the AI
                {"role": "system", "content": f"You are a helpful assistant that translates text into {target_language}."},
                # The user prompt contains the actual text to be processed
                {"role": "user", "content": text}
            ],
            temperature=0.3 # Lower temperature makes the output more focused and deterministic
        )
        
        # 4. Extract and return the text from the response
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    print("=== Beginner's AI Translation Quick Start ===")
    print("Make sure you have set OPENAI_API_KEY in your .env file.")
    print("Type 'quit' at any time to exit.\n")
    
    # Ask the user for the target language once
    target_lang = input("Enter the language you want to translate to (e.g., French, Japanese): ")
    
    if target_lang.lower() == 'quit':
        exit()
        
    print(f"\nGreat! I will now translate your text into {target_lang}.")
    
    # 5. Start a simple chat loop
    while True:
        user_input = input("\nEnter text to translate: ")
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not user_input.strip():
            continue
            
        print("Translating...")
        translation = translate_text(user_input, target_lang)
        
        print(f"\n=> Translation: {translation}")
