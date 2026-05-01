import pygame  # For audio playback
import random  # For choosing random chat responses
import asyncio  # For async handling
import edge_tts  # For TTS using Edge voices
import os  # For file operations
from dotenv import dotenv_values  # For loading .env variables

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-IN-PrabhatNeural")  # Fallback voice if not found

# File path where speech will be saved
file_path = r"Data\speech.mp3"

# Asynchronous function to convert text to audio
async def TextToAudioFile(text):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)  # Remove old speech file if exists

        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)

    except Exception as e:
        print(f"TextToAudioFile Error: {e}")

# Function to play the speech file using pygame
def TTS(text, func=lambda r=None: True):
    while True:
        try:
            # Generate audio from text
            asyncio.run(TextToAudioFile(text))

            # Play the audio using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            # Keep playing while busy, unless func() says stop
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)

            return True

        except Exception as e:
            print(f"Error in TTS: {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in cleanup: {e}")

# Function to manage long text responses with split logic
def TextToSpeech(text, func=lambda r=None: True):
    sentences = str(text).split(".")
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(sentences) > 4 and len(text) >= 250:
        TTS(" ".join(sentences[:2]) + ".", func)
        TTS(random.choice(responses), func)
    else:
        TTS(text, func)

# Run in terminal
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        TextToSpeech(user_input)