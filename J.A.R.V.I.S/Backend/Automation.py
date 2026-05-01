# Automation.py
# -------------------------------
# Handles system-level automation: open/close apps, search, YouTube, content creation, etc.

# Import required libraries
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Setup Groq client
client = Groq(api_key=GroqAPIKey)

# User-Agent for scraping
useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/100.0.4896.75 Safari/537.36"
)

# Global message context for AI
messages = []
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.getenv('USERNAME', 'User')}. "
               f"You are an intelligent content writer. "
               f"Write professional and creative text for letters, codes, essays, songs, poems, and more."
}]


# -----------------------------
# 🔍 GOOGLE SEARCH
def GoogleSearch(topic):
    try:
        search(topic)
        return True
    except Exception as e:
        print(f"[red]GoogleSearch Error:[/red] {e}")
        return False


# -----------------------------
# 🧠 AI CONTENT GENERATION
def Content(topic):

    def open_notepad(file_path):
        subprocess.Popen(["notepad.exe", file_path])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
        )

        answer = ""
        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                answer += delta.content

        answer = answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": answer})
        return answer

    topic_clean = topic.replace("content ", "").strip()
    content_text = ContentWriterAI(topic_clean)

    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{topic_clean.replace(' ', '_')}.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_text)

    open_notepad(file_path)
    return True


# -----------------------------
# ▶️ YOUTUBE FUNCTIONS
def YouTubeSearch(topic):
    try:
        url = f"https://www.youtube.com/results?search_query={topic}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"[red]YouTubeSearch Error:[/red] {e}")
        return False


def PlayYoutube(query):
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"[red]PlayYoutube Error:[/red] {e}")
        return False


# -----------------------------
# 💻 APP CONTROL
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        # fallback: search and open via browser
        def extract_links(html):
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)
            return [l["href"] for l in links if l["href"].startswith("http")]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True


def CloseApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]CloseApp Error:[/red] {e}")
        return False


# -----------------------------
# ⚙️ SYSTEM CONTROLS
def System(command):
    try:
        if command == "mute":
            keyboard.press_and_release("volume mute")
        elif command == "unmute":
            keyboard.press_and_release("volume mute")
        elif command == "volume up":
            keyboard.press_and_release("volume up")
        elif command == "volume down":
            keyboard.press_and_release("volume down")
        else:
            print(f"[yellow]Unknown system command:[/yellow] {command}")
        return True
    except Exception as e:
        print(f"[red]System Error:[/red] {e}")
        return False


# -----------------------------
# 🤖 COMMAND TRANSLATOR
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        cmd = command.lower().strip()

        if cmd.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, cmd.replace("open ", "")))
        elif cmd.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd.replace("close ", "")))
        elif cmd.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd.replace("play ", "")))
        elif cmd.startswith("content "):
            funcs.append(asyncio.to_thread(Content, cmd.replace("content ", "")))
        elif cmd.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd.replace("google search ", "")))
        elif cmd.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd.replace("youtube search ", "")))
        elif cmd.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd.replace("system ", "")))
        else:
            print(f"[yellow]No function found for:[/yellow] {cmd}")

    results = await asyncio.gather(*funcs, return_exceptions=True)
    return results


# -----------------------------
# 🧠 MAIN AUTOMATION FUNCTION
async def Automation(commands: list[str]):
    await TranslateAndExecute(commands)
    return True


# -----------------------------
# 🧩 TEST RUN
if __name__ == "__main__":
    asyncio.run(Automation([
        "open chrome",
        "play mithe raas se by kinjal dave",
        "content poem about friendship",
        "system mute"
    ]))
