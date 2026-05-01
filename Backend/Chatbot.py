from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import re
from rich.console import Console
from rich.panel import Panel

# Initialize console for better visuals
console = Console()

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "J.A.R.V.I.S")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# ✅ Updated model (old model deprecated)
GROQ_MODEL = "llama-3.3-70b-versatile"  # Recommended replacement for llama3-70b-8192

# System prompt
System = (
    f"Hello, I am {Username}. You are a highly intelligent, polite, and professional AI chatbot named {Assistantname}. "
    "You have access to real-time information and web data.\n"
    "Respond in a professional, concise, helpful, and respectful tone. "
    "Avoid emotional expression or unnecessary elaboration. Only respond in English."
)

# Load or initialize chat log
try:
    with open(r"Data\\ChatLog.json", "r") as f:
        messages = load(f)
except:
    messages = []
    with open(r"Data\\ChatLog.json", "w") as f:
        dump(messages, f)

# Google Search
def GoogleSearch(query):
    try:
        results = list(search(query, num_results=5))
        Answer = f"Top search results for '{query}':\n"
        for url in results:
            Answer += f"- {url}\n"
        return Answer.strip()
    except Exception as e:
        return f"⚠️ Google search failed: {str(e)}"

# Clean up answer text
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join([line for line in lines if line.strip()])

# Static system instructions
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I assist you today?"}
]

# Real-time information generator
def Information():
    now = datetime.datetime.now()
    return (
        "Real-time Information:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

# Exit message detection
def is_exit_message(text):
    exit_phrases = [
        "exit", "quit", "bye", "goodbye", "see you", "see ya",
        "thanks bye", "thank you bye", "talk later", "later", "farewell",
        "stop", "end session", "end chat", "close"
    ]
    normalized = text.strip().lower()
    for phrase in exit_phrases:
        if re.search(rf'\b{re.escape(phrase)}\b', normalized):
            return True
    return False

# Core chat function
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load message history
    with open(r"Data\\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    # Optional live web context
    web_context = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": web_context})

    console.print("[cyan]🧠 Processing your request...[/cyan]")

    Answer = ""
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

    except Exception as e:
        console.print(f"[red]⚠️ Groq API Error:[/red] {e}")
        return "I'm sorry, I encountered an issue connecting to the AI model."

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save updated chat history
    with open(r"Data\\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()

    return AnswerModifier(Answer)

# Main loop
if __name__ == "__main__":
    console.print(
        Panel.fit(
            f"[bold cyan]🛰️  {Assistantname} Online[/bold cyan]\n[dim]Ask me anything, {Username}...[/dim]",
            title="🤖 AI Assistant",
            border_style="bright_magenta"
        )
    )

    while True:
        try:
            prompt = input("\n🗣️  You: ").strip()

            if is_exit_message(prompt):
                console.print("\n[bold red]👋 Session ended. Goodbye![/bold red]")
                break

            console.print("\n[bright_black]⏳ Thinking...[/bright_black]\n")
            response = RealtimeSearchEngine(prompt)
            console.print(Panel.fit(response, title=f"[green]🧠 {Assistantname}[/green]", border_style="bright_green"))

        except KeyboardInterrupt:
            console.print("\n[bold red]❌ Interrupted by user. Exiting...[/bold red]")
            break
        except Exception as e:
            console.print(f"[red]⚠️ Error:[/red] {e}")
