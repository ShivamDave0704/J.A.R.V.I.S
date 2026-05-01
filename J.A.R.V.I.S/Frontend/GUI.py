# Frontend/GUI.py

import sys
import os
from pathlib import Path

# ✅ Ensure the Backend folder is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

# ✅ Correct imports (case-sensitive)
from Backend.Chatbot import Chatbot as chat_with_jarves
from Backend.SpeechToText import recognize_speech
from Backend.Automation import handle_automation
from Backend.RealtimeSearchEngine import perform_realtime_search
from Backend.ImageGeneration import generate_image

# File paths
BASE_PATH = Path(__file__).resolve().parent.parent
RESPONSE_FILE = BASE_PATH / "Frontend" / "Files" / "Responce.data"


class JARVESInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.E.S - AI Assistant")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #0f0f0f; color: #00ffcc; font-size: 16px;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Animated GIF
        self.gif_label = QLabel()
        self.movie = QMovie(str(BASE_PATH / "frontend" / "graphics" / "jarvis.gif"))
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)

        # Chat area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input field + buttons
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command here...")
        self.input_field.returnPressed.connect(self.process_input)
        input_layout.addWidget(self.input_field)

        self.mic_button = QPushButton("🎤")
        self.mic_button.clicked.connect(self.voice_input)
        input_layout.addWidget(self.mic_button)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def append_chat(self, sender, text):
        self.chat_display.append(f"<b>{sender}:</b> {text}")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def process_input(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        self.append_chat("You", user_input)
        self.input_field.clear()

        response = self.get_response(user_input)
        self.append_chat("JARVES", response)
        self.save_response(response)

    def voice_input(self):
        self.append_chat("System", "Listening via microphone...")
        voice_command = recognize_speech()
        self.append_chat("You (voice)", voice_command)

        response = self.get_response(voice_command)
        self.append_chat("JARVES", response)
        self.save_response(response)

    def get_response(self, query):
        query_lower = query.lower()

        # Handle automation tasks
        if "open" in query_lower or "close" in query_lower or "volume" in query_lower or "shutdown" in query_lower:
            return handle_automation(query)

        # Real-time search
        elif "search" in query_lower or "who is" in query_lower or "what is" in query_lower:
            return perform_realtime_search(query)

        # Image generation
        elif "generate image" in query_lower:
            return generate_image(prompt=query)

        # Default: use chatbot
        else:
            return chat_with_jarves(query)

    def save_response(self, response):
        with open(RESPONSE_FILE, "w", encoding="utf-8") as file:
            file.write(response)

def run_gui():
    app = QApplication(sys.argv)
    window = JARVESInterface()
    window.show()
    sys.exit(app.exec_())
