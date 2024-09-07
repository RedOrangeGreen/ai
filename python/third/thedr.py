"""
Application Details
-------------------
Name: The Doctor
Objective: Diagnose Medical Symptoms
AI Chatbot (Free): https://www.perplexity.ai
Run Time AI SDK/LLM Model (Free): GPT4All Python SDK/Phi-3-mini-4k-instruct.Q4_0.gguf, https://docs.gpt4all.io/gpt4all_python/home.html
Development Environment: Ubuntu 24.04.01 LTS

Specification (Ask AI Chatbot These Questions To Generate Code)
---------------------------------------------------------------
What are the common questions a doctors asks to determine symptoms?
Show me a python application to ask these questions and store the symptoms
Add a PyQt6 wrapper
Add code to create a single question which is passed into the GPT4All SDK to ask for a suggested diagnosis given all the symptoms. Use the "Phi-3-mini-4k-instruct.Q4_0.gguf" LLM model (exact case as shown)
Enhance with a button to load the LLM model
Enhance with a "Patient Diagnosis" summary which shows the answer

Using The Generated Code
------------------------
sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate
pip cache purge
pip install PyQt6
pip install gpt4all

gsettings set org.gnome.mutter check-alive-timeout 600000
python3 thedr.py

deactivate
rm -rf ./myenv
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QScrollArea
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from gpt4all import GPT4All

class ModelLoader(QThread):
    finished = pyqtSignal(GPT4All)
    error = pyqtSignal(str)

    def run(self):
        try:
            model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
            self.finished.emit(model)
        except Exception as e:
            self.error.emit(str(e))

class SymptomGatherer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.symptoms = {}
        self.model = None

    def initUI(self):
        main_layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        self.questions = [
            "What are your main symptoms?",
            "When did your symptoms start?",
            "How long have you been experiencing these symptoms?",
            "On a scale of 1-10, how severe are your symptoms?",
            "How often do you experience these symptoms?",
            "Does anything seem to trigger or worsen your symptoms?",
            "Does anything make your symptoms better?",
            "Are you experiencing any other associated symptoms?",
            "How are these symptoms affecting your daily activities?",
            "Have you experienced similar symptoms before?",
            "Are you currently taking any medications?",
            "Have there been any recent changes or stressors in your life?"
        ]

        self.inputs = []

        for question in self.questions:
            layout.addWidget(QLabel(question))
            input_field = QLineEdit()
            layout.addWidget(input_field)
            self.inputs.append(input_field)

        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.submit_symptoms)
        self.submit_button.setEnabled(False)
        layout.addWidget(self.submit_button)

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        layout.addWidget(QLabel("Symptom Summary:"))
        layout.addWidget(self.summary)

        self.diagnosis = QTextEdit()
        self.diagnosis.setReadOnly(True)
        layout.addWidget(QLabel("AI Response:"))
        layout.addWidget(self.diagnosis)

        self.patient_diagnosis = QTextEdit()
        self.patient_diagnosis.setReadOnly(True)
        layout.addWidget(QLabel("Patient Diagnosis:"))
        layout.addWidget(self.patient_diagnosis)

        self.load_model_button = QPushButton('Load LLM Model')
        self.load_model_button.clicked.connect(self.load_model)
        layout.addWidget(self.load_model_button)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.setWindowTitle('Symptom Gatherer')
        self.setGeometry(300, 300, 600, 800)

    def load_model(self):
        self.load_model_button.setEnabled(False)
        self.load_model_button.setText('Loading...')
        
        self.loader = ModelLoader()
        self.loader.finished.connect(self.on_model_loaded)
        self.loader.error.connect(self.on_model_error)
        self.loader.start()

    def on_model_loaded(self, model):
        self.model = model
        self.load_model_button.setText('Model Loaded')
        self.submit_button.setEnabled(True)
        QMessageBox.information(self, "Success", "LLM model loaded successfully!")

    def on_model_error(self, error_msg):
        self.load_model_button.setEnabled(True)
        self.load_model_button.setText('Load LLM Model')
        QMessageBox.critical(self, "Error", f"Failed to load model: {error_msg}")

    def submit_symptoms(self):
        self.symptoms = {}
        for question, input_field in zip(self.questions, self.inputs):
            key = question.lower().replace(" ", "_").replace("?", "")
            self.symptoms[key] = input_field.text()

        self.display_symptoms()
        self.get_diagnosis()

    def display_symptoms(self):
        summary = "Symptom Summary:\n\n"
        for question, answer in self.symptoms.items():
            summary += f"{question.replace('_', ' ').capitalize()}: {answer}\n"
        
        self.summary.setText(summary)

    def get_diagnosis(self):
        if self.model is None:
            QMessageBox.warning(self, "Warning", "Please load the LLM model first.")
            return

        prompt = f"""Given the following symptoms, please suggest a possible diagnosis. 
        Provide your response in the following format:
        Possible Diagnosis: [Your suggested diagnosis]
        Explanation: [A brief explanation of why you suggest this diagnosis]
        Recommended Actions: [Suggested next steps for the patient]

        Remember, this is not a definitive medical opinion and the patient should consult a healthcare professional for accurate diagnosis and treatment.

        Symptoms:
        {self.summary.toPlainText()}

        Diagnosis:"""
        
        response = self.model.generate(prompt, max_tokens=300)
        
        self.diagnosis.setText(response)
        self.format_patient_diagnosis(response)

    def format_patient_diagnosis(self, ai_response):
        sections = ["Possible Diagnosis:", "Explanation:", "Recommended Actions:"]
        formatted_diagnosis = ""

        for section in sections:
            start = ai_response.find(section)
            if start != -1:
                end = ai_response.find(next((s for s in sections if s != section), ""), start)
                if end == -1:
                    end = len(ai_response)
                content = ai_response[start:end].strip()
                formatted_diagnosis += f"<b>{content.split(':', 1)[0]}:</b><br>{content.split(':', 1)[1].strip()}<br><br>"

        self.patient_diagnosis.setHtml(formatted_diagnosis)

def main():
    app = QApplication(sys.argv)
    ex = SymptomGatherer()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()