"""
Using Ollama From Python To Create A Simple, Locally Running, Graphical Chat Interface
======================================================================================

Platform
--------
Ubuntu Linux 24.04.1 LTS

Setting Up
-----------
Download Ollama Maintenance Tool from https://redorangegreen.github.io/ai/ollama/maintenancetool.html
chmod +x ./ollama.sh
./ollama.sh
  1. Install Ollama
  2. Chat With Ollama (Using Default Model: llama3.2:1b)
  /bye
  5. Exit
sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate
pip cache purge
pip install PyQt6 ollama

Using
-----
source myenv/bin/activate
python3 useollama.py

Cleaning Up
-----------
deactivate
rm -rf ./myenv

Development And Testing
-----------------------
All source code was AI generated by Copilot answers to Pilot questions.
Pilot: AI Playground (Quasimodo), https://redorangegreen.github.io/ai
Copilot: Perplexity AI Free, https://www.perplexity.ai

Test Questions
--------------
Why is the sky blue?
Why is the sea blue?
Show me a C++ hello world which calls a class containing sum() and mult() methods, just the code, no explanation
"""
import sys
import ollama
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLineEdit, QComboBox, QDialog, QLabel,
                             QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model, question):
        super().__init__()
        self.model = model
        self.question = question

    def run(self):
        try:
            response = ollama.chat(model=self.model, messages=[
                {
                    'role': 'user',
                    'content': self.question,
                },
            ])
            content = response['message']['content']
            self.finished.emit(content)
        except Exception as e:
            self.error.emit(str(e))

class CustomDialog(QDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #888888;
            }
            #titleLabel {
                background-color: #f0f0f0;
                border-bottom: 1px solid #888888;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #888888;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title_bar = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_bar.addWidget(title_label)
        
        close_button = QPushButton("X")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        title_bar.addWidget(close_button)
        
        layout.addLayout(title_bar)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        self.setLayout(layout)

    def showEvent(self, event):
        if self.parent():
            self.move(self.parent().geometry().center() - self.rect().center())
        super().showEvent(event)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

class SimpleLoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #888888;
            }
            QLabel {
                font-size: 16px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        self.message_label = QLabel("Generating response...")
        
        font = QFont("Courier")
        font.setPointSize(16)
        self.message_label.setFont(font)
        
        self.message_label.setFixedSize(250, 40)
        
        layout.addWidget(self.message_label)
        
        self.setLayout(layout)
        
        self.setFixedSize(300, 80)
        
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)

    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        dots_text = '.' * self.dots
        self.message_label.setText(f"Generating response{dots_text:<3}")

    def showEvent(self, event):
        if self.parent():
            self.move(self.parent().geometry().center() - self.rect().center())
        super().showEvent(event)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 330)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        title_bar = QWidget(self)
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            background-color: #3498db;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel("About Ollama Chat Interface")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_bar_layout.addWidget(title_label)
        
        close_button = QPushButton("X")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 10px;
                font-family: Arial;
                font-size: 16px;
                font-weight: bold;
                padding: 0;
                margin: 0;
                line-height: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)
        
        main_layout.addWidget(title_bar)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Ollama Chat Interface")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px;
        """)
        
        content_layout.addWidget(title_label)
        
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        author_label = QLabel("Created by Your Name")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        description_label = QLabel("This application provides a user-friendly interface "
                                   "for interacting with Ollama AI models.")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        
        content_layout.addWidget(version_label)
        content_layout.addWidget(author_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(description_label)
        content_layout.addSpacing(20)
        content_layout.addWidget(ok_button)
        
        main_layout.addLayout(content_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.oldPos = self.pos()
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama Chat Interface")
        self.setGeometry(100, 100, 800, 600)

        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Enter your question here...")
        self.question_input.returnPressed.connect(self.send_question)
        input_layout.addWidget(self.question_input, 1)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3.2:1b"])
        input_layout.addWidget(self.model_selector)

        self.print_mode = QComboBox()
        self.print_mode.addItems(["Word-by-Word", "Full"])
        input_layout.addWidget(self.print_mode)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_question)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.word_timer = QTimer(self)
        self.word_timer.timeout.connect(self.print_next_word)
        self.current_words = []

        self.loading_dialog = None

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        exit_action = file_menu.addAction("&Exit")
        exit_action.triggered.connect(self.close)

        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)

        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def send_question(self):
        question = self.question_input.text()
        if question:
            self.append_to_chat("You", question)
            self.question_input.clear()
            self.get_and_print_response(question)

    def get_and_print_response(self, question):
        model = self.model_selector.currentText()
        
        self.loading_dialog = SimpleLoadingDialog(self)
        self.loading_dialog.show()

        self.worker = AIWorker(model, question)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def handle_response(self, content):
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        if self.print_mode.currentText() == "Full":
            self.append_to_chat("AI", content)
        else:
            self.current_words = content.split()
            self.chat_display.insertPlainText("AI: ")
            self.word_timer.start(100)

    def handle_error(self, error_message):
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        if "model not found" in error_message:
            model = self.model_selector.currentText()
            dialog = CustomDialog(self, "Model Not Found", f"The model '{model}' was not found. Please pull it first using 'ollama pull {model}'.")
        else:
            dialog = CustomDialog(self, "Error", f"An error occurred: {error_message}")
        
        dialog.exec()

    def print_next_word(self):
        if self.current_words:
            word = self.current_words.pop(0)
            self.chat_display.insertPlainText(word + " ")
            self.scroll_to_bottom()
        else:
            self.word_timer.stop()
            self.chat_display.insertPlainText("\n\n")
            self.scroll_to_bottom()

    def append_to_chat(self, sender, message):
        self.chat_display.append(f"{sender}: {message}\n")
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()