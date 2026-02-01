import sys
import subprocess
import shutil
import os
import gc
import atexit
from pathlib import Path
import html
from datetime import datetime
import webbrowser
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLineEdit, QPushButton, QLabel, QPlainTextEdit, 
                               QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor
from urllib.parse import quote

# Fix for Linux XCB issues - add at top
if os.name == 'posix':
    os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')

# Global LLM instance to manage lifecycle
_global_llm = None

def ensure_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name

    try:
        return __import__(import_name)
    except ModuleNotFoundError:
        if not shutil.which(sys.executable):
            raise RuntimeError("Python executable not found.")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        except:
            raise RuntimeError("pip not available. Run the setup script first.")

        print("Installing " + package_name + "...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return __import__(import_name)

def cleanup_llm():
    """Global cleanup to prevent sampler errors"""
    global _global_llm
    if _global_llm is not None:
        try:
            _global_llm.close()
            del _global_llm
            gc.collect()
        except:
            pass
        _global_llm = None

atexit.register(cleanup_llm)

class Worker(QThread):
    progress = Signal(int)
    log_message = Signal(str)
    finished = Signal(str, str)  # html_file, wikipedia_url
    error = Signal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query
        self.wikipedia = ensure_package("wikipedia")
        global _global_llm
        if _global_llm is None:
            self.llama_cpp = ensure_package("llama_cpp")
        else:
            self.llama_cpp = None

    def run(self):
        global _global_llm
        try:
            self.log("Starting analysis for: '" + self.query + "'")
            self.progress.emit(5)

            results = self.wikipedia.search(self.query, results=5)
            if not results:
                self.error.emit("No Wikipedia results found for: " + self.query)
                return
            
            page_title = results[0]
            self.log("Top result: '" + page_title + "'")
            self.progress.emit(30)

            main_summary = self.get_summary_safe(page_title)
            if not main_summary:
                self.error.emit("Could not get summary for: " + page_title)
                return
            
            wikipedia_url = self.get_wikipedia_url(page_title)
            self.progress.emit(50)

            # Load LLM only once globally
            if _global_llm is None:
                self.log("Loading LLM model from ~/Downloads...")
                _global_llm = self.load_llm_model()
                self.progress.emit(70)
            else:
                self.log("Using cached LLM model...")
                self.progress.emit(70)

            self.log("Generating AI answer: 'What is " + page_title + "'...")
            ai_answer = self.generate_ai_answer(page_title, main_summary)
            self.progress.emit(80)

            # Generate 1 AI Interesting Fact
            self.log("Generating AI interesting fact about " + page_title + "...")
            ai_fact = self.generate_ai_interesting_fact(page_title, main_summary)
            self.progress.emit(90)

            self.log("Generating HTML report...")
            html_report = self.generate_summary_report(page_title, main_summary, wikipedia_url, ai_answer, ai_fact)
            
            output_file = Path.cwd() / "wikipedia_summary.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            self.progress.emit(100)
            self.finished.emit(str(output_file), wikipedia_url)
            
        except Exception as e:
            self.error.emit(str(e))

    def get_summary_safe(self, title):
        self.log("Fetching summary for '" + title + "'...")
        try:
            summary = self.wikipedia.summary(title, sentences=4, auto_suggest=False)
            return summary
        except:
            return None

    def get_wikipedia_url(self, title):
        encoded_title = quote(title.replace(' ', '_'))
        return f"https://en.wikipedia.org/wiki/{encoded_title}"

    def load_llm_model(self):
        """Load model once globally from ~/Downloads"""
        model_path = Path.home() / "Downloads" / "gemma-3-1b-it-Q8_0.gguf"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"LLM model not found at {model_path}\n"
                f"Run setup.sh first to download it to ~/Downloads/"
            )
        
        self.log(f"Loading model: {model_path}")
        llm = self.llama_cpp.Llama(
            model_path=str(model_path),
            n_ctx=2048,
            verbose=False
        )
        self.log("✅ LLM model loaded successfully!")
        return llm

    def generate_ai_answer(self, title, summary):
        """Generate AI answer using global LLM"""
        global _global_llm
        prompt = f"""What is '{title}'? Give a clear, concise explanation in 3-4 sentences.

Wikipedia summary: {summary}

Answer:"""

        self.log("Running LLM inference...")
        try:
            response = _global_llm(
                prompt,
                max_tokens=150,
                temperature=0.7,
                echo=False
            )
            ai_text = response["choices"][0]["text"].strip()
        except Exception as e:
            self.log(f"LLM error, using fallback: {str(e)[:100]}")
            ai_text = f"AI: '{title}' is an important topic covered in Wikipedia with {len(summary)} words of detailed explanation."
        
        return html.escape(ai_text).replace('\\n', '<br>')

    def generate_ai_interesting_fact(self, subject, summary):
        """Generate 1 interesting fact using 'What is an interesting fact about X?'"""
        global _global_llm
        
        fact_prompt = f"""What is an interesting fact about '{subject}'?

Wikipedia context: {summary}

Give exactly ONE interesting fact in 1-2 sentences."""

        try:
            self.log("Running LLM inference for interesting fact...")
            response = _global_llm(
                fact_prompt, 
                max_tokens=100, 
                temperature=0.6,
                echo=False
            )
            fact_text = response["choices"][0]["text"].strip()
        except Exception as e:
            self.log(f"Fact generation error, using fallback: {str(e)[:80]}")
            fact_text = f"An interesting fact about {subject} is that it plays a significant role in modern understanding."

        return html.escape(fact_text).replace('\\n', '<br>')

    def generate_summary_report(self, main_title, main_summary, wikipedia_url, ai_answer, ai_fact):
        """FIXED: Uses f-strings instead of .format() to avoid index errors"""
        main_summary_html = html.escape(main_summary).replace('\\n', '<br>')
        main_title_escaped = html.escape(main_title)
        timestamp = datetime.now().strftime("%B %d, %Y %H:%M")
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wikipedia Summary - {main_title_escaped}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 900px; margin: 0 auto; background: rgba(255,255,255,0.95); border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; backdrop-filter: blur(10px); }}
        .header {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 40px 40px 20px; text-align: center; }}
        .header h1 {{ margin: 0 0 15px 0; font-size: 2.8em; font-weight: 800; background: linear-gradient(45deg, #fff, #f0f8ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .subject-title {{ font-size: 2.2em !important; font-weight: 700 !important; margin: 0 0 20px 0 !important; color: #2c3e50 !important; }}
        .main-content {{ padding: 40px; }}
        .summary-section, .ai-section, .fact-section {{ margin-bottom: 40px; }}
        h2 {{ color: #2c3e50; border-bottom: 4px solid #3498db; padding-bottom: 15px; font-size: 1.8em; margin-bottom: 25px; }}
        .summary-text, .ai-text, .fact-text {{ line-height: 1.8; font-size: 1.2em; background: rgba(255,255,255,0.8); padding: 35px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
        .summary-text {{ border-left: 6px solid #3498db; }}
        .ai-text {{ border-left: 6px solid #00cec9; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }}
        .fact-text {{ border-left: 6px solid #e74c3c; background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); }}
        .wiki-link-section {{ text-align: center; margin: 40px 0; }}
        .wiki-link-btn {{ display: inline-block; background: linear-gradient(45deg, #3498db, #2980b9); color: white; padding: 18px 40px; border-radius: 50px; text-decoration: none; font-size: 1.3em; font-weight: 600; box-shadow: 0 10px 30px rgba(52, 152, 219,0.4); transition: all 0.3s ease; border: none; cursor: pointer; }}
        .wiki-link-btn:hover {{ transform: translateY(-3px); box-shadow: 0 15px 40px rgba(52, 152,219,0.6); }}
        .footer {{ background: rgba(0,0,0,0.2); color: rgba(255,255,255,0.9); padding: 25px; text-align: center; font-size: 1em; }}
        @media (max-width: 768px) {{ 
            .main-content {{ padding: 20px; }} 
            .summary-text, .ai-text, .fact-text {{ padding: 25px 20px; font-size: 1.1em; }}
            .subject-title {{ font-size: 1.8em !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 Wikipedia + AI</h1>
            <p><strong><span class="subject-title">{main_title_escaped}</span></strong></p>
        </div>
        <div class="main-content">
            <div class="summary-section">
                <h2>📄 Wikipedia Summary</h2>
                <div class="summary-text">{main_summary_html}</div>
            </div>
            <div class="wiki-link-section">
                <h2>🔗 Source Article</h2>
                <a href="{wikipedia_url}" class="wiki-link-btn" target="_blank">🢣 Open Full Wikipedia Article</a>
            </div>
            <div class="ai-section">
                <h2>🤖 AI Answer: "What is {main_title_escaped}?"</h2>
                <div class="ai-text">{ai_answer}</div>
            </div>
            <div class="fact-section">
                <h2>🤖 AI Interesting Fact: {main_title_escaped}</h2>
                <div class="fact-text">{ai_fact}</div>
            </div>
        </div>
        <div class="footer">
            <p>Wikipedia + Gemma-3-1B LLM | {timestamp}</p>
        </div>
    </div>
</body>
</html>'''
        return html_template

    def log(self, message):
        self.log_message.emit(message)

class WikipediaResearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wikipedia + AI")
        self.setGeometry(100, 100, 900, 700)
        self.worker = None
        self.init_ui()
        self.load_recent_query()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        title = QLabel("Wikipedia + AI")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter topic (e.g., 'computer')")  # CHANGED: 'computer'
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.returnPressed.connect(self.start_research)
        input_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Get Info")
        self.search_button.setFont(QFont("Arial", 12))
        self.search_button.clicked.connect(self.start_research)
        self.search_button.setMinimumWidth(100)
        input_layout.addWidget(self.search_button)
        layout.addLayout(input_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.log_output = QPlainTextEdit()
        self.log_output.setMaximumBlockCount(1000)
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("AI generating answer and interesting fact...")
        layout.addWidget(QLabel("Progress Log:"))
        layout.addWidget(self.log_output)
        
        self.statusBar().showMessage("Wikipedia lookup + AI explanation + interesting fact!")

    def load_recent_query(self):
        try:
            with open("recent_query.txt", "r") as f:
                query = f.read().strip()
                if query:
                    self.search_input.setText(query)
        except:
            self.search_input.setText("computer")  # CHANGED: Default to 'computer'

    def save_recent_query(self, query):
        try:
            with open("recent_query.txt", "w") as f:
                f.write(query)
        except:
            pass

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.appendPlainText(f"{timestamp} | {message}")
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def start_research(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Input Required", "Please enter a search term.")
            return
        
        self.save_recent_query(query)
        self.search_button.setEnabled(False)
        self.search_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_output.clear()
        
        self.statusBar().showMessage("Getting Wikipedia + AI info...")
        self.worker = Worker(query)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log_message.connect(self.log)
        self.worker.finished.connect(self.research_finished)
        self.worker.error.connect(self.research_error)
        self.worker.start()

    def research_finished(self, html_file, wikipedia_url):
        """NO AUTO-BROWSER: HTML only - Wikipedia option REMOVED"""
        self.search_button.setEnabled(True)
        self.search_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"✅ Ready! {html_file}")
        
        self.log(f"✅ HTML saved: {html_file}")
        self.log("🎉 Ready! No browser opened automatically.")
        
        # HTML-ONLY dialog - Wikipedia option REMOVED
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("✅ Complete!")
        msg.setText("Wikipedia + AI report ready!")
        msg.setInformativeText(f"📄 HTML saved:\n{html_file}")
        
        # ONLY HTML and Close buttons
        html_btn = msg.addButton("🖥️ Open HTML", QMessageBox.ActionRole)
        msg.addButton("❌ Close", QMessageBox.RejectRole)
        
        msg.exec()
        
        # Handle HTML choice only
        if msg.clickedButton() == html_btn:
            webbrowser.open('file://' + os.path.abspath(html_file))
            self.log("✅ User opened HTML file")

    def research_error(self, error_msg):
        self.search_button.setEnabled(True)
        self.search_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error occurred")
        self.log(f"❌ Error: {error_msg}")
        QMessageBox.critical(self, "Error", error_msg)

    def closeEvent(self, event):
        """Clean up on app close"""
        cleanup_llm()
        event.accept()

def main():
    atexit.register(cleanup_llm)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = WikipediaResearchApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
