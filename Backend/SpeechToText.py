import speech_recognition as sr
import time
import os

mic_status_path = "Frontend/Files/Mic.data"
last_status = None

def read_mic_status():
    with open(mic_status_path, "r") as f:
        status = f.read().strip().lower()
        # Convert 'true' -> 'on', 'false' -> 'off' for internal logic
        if status == "true":
            return "on"
        elif status == "false":
            return "off"
        else:
            return "off"  # default fallback if something else is written

def SpeechRecognition():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎙️ Mic is ON. Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        raw_text = recognizer.recognize_google(audio)
        print(f"🗣️ Raw: {raw_text}")
        print(f"✅ Recognized: {raw_text.capitalize()}.")
        return raw_text
    except sr.UnknownValueError:
        print("❌ Sorry, I couldn't understand.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")
        return ""

# 🔁 Start loop
print("🔁 Voice system is running. Say something when mic is ON (Mic.data = 'true')")

try:
    while True:
        mic_status = read_mic_status()

        if mic_status != last_status:
            if mic_status == "on":
                print("🎙️ Mic is ON. Listening...")
            else:
                print("🛑 Mic is OFF. Waiting to be turned ON...")
            last_status = mic_status

        if mic_status == "on":
            output = SpeechRecognition()
            # You can add extra logic here to use output
        else:
            time.sleep(0.5)  # Reduce CPU usage when off

except KeyboardInterrupt:
    print("\n🛑 Voice recognition stopped by user.")
