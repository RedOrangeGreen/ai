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
Show me a python application which ask these questions and store the symptoms
Add a PyQt6 wrapper
Add code to create a single question which is passed into the GPT4All SDK to ask for a suggested diagnosis given all the symptoms. Use the "Phi-3-mini-4k-instruct.Q4_0.gguf" LLM model (exact case as shown)
Enhance with buttons to load and unload the LLM model
Enhance with a "Patient Diagnosis" summary which shows the answer sumamrised in one sentence

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
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QHBoxLayout
from PyQt6.QtCore import Qt
from gpt4all import GPT4All

class SymptomChecker:
    def __init__(self):
        self.symptoms = {}
        self.model = None

    def add_symptom(self, key, value):
        self.symptoms[key] = value

    def get_symptoms(self):
        return self.symptoms

    def load_model(self):
        self.model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
        return "Model loaded successfully"

    def unload_model(self):
        if self.model:
            del self.model
            self.model = None
            return "Model unloaded successfully"
        return "No model currently loaded"

    def get_diagnosis_suggestion(self):
        if not self.model:
            return "Error: Model not loaded", "Error: Model not loaded"

        symptoms_list = [f"{key}: {value}" for key, value in self.symptoms.items() if value]
        prompt = f"Given the following symptoms: {', '.join(symptoms_list)}. What is a possible diagnosis? Provide a brief explanation for your suggestion."

        with self.model.chat_session():
            detailed_response = self.model.generate(prompt, max_tokens=200)

        summary_prompt = f"Summarize the following diagnosis in one sentence: {detailed_response}"
        with self.model.chat_session():
            summary_response = self.model.generate(summary_prompt, max_tokens=50)

        return detailed_response, summary_response

class SymptomCheckerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.checker = SymptomChecker()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Symptom Checker')
        self.setGeometry(100, 100, 600, 600)

        layout = QVBoxLayout()

        # Model control buttons
        model_buttons_layout = QHBoxLayout()
        self.load_model_button = QPushButton('Load Model')
        self.load_model_button.clicked.connect(self.load_model)
        self.unload_model_button = QPushButton('Unload Model')
        self.unload_model_button.clicked.connect(self.unload_model)
        model_buttons_layout.addWidget(self.load_model_button)
        model_buttons_layout.addWidget(self.unload_model_button)
        layout.addLayout(model_buttons_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.questions = [
            ("main_symptoms", "What are your main symptoms?"),
            ("onset", "When did your symptoms start?"),
            ("progression", "Have your symptoms gotten better or worse over time?"),
            ("frequency", "Are the symptoms constant or do they come and go?"),
            ("factors", "What makes the symptoms better or worse?"),
            ("severity", "On a scale of 1-10, how severe are the symptoms?"),
            ("impact", "How do the symptoms affect your daily activities?"),
            ("family_history", "Do you have a family history of similar symptoms or conditions?"),
            ("recent_procedures", "Have you had any procedures or major illnesses in the past 12 months?"),
            ("medications", "What medications, vitamins, and supplements are you currently taking?"),
            ("allergies", "Do you have any allergies?"),
            ("substance_use", "Do you use tobacco, alcohol, or illicit drugs? If so, please specify:"),
            ("sexual_activity", "Are you sexually active?"),
            ("diet_sleep", "How would you describe your diet and sleep patterns?"),
            ("stress", "Have there been any major stresses or changes in your life recently?"),
            ("treatments_tried", "Have you tried any treatments or remedies for these symptoms?"),
            ("other_concerns", "Are there any other symptoms or health concerns you want to discuss?")
        ]

        self.inputs = {}
        for key, question in self.questions:
            label = QLabel(question)
            input_field = QLineEdit()
            self.inputs[key] = input_field
            scroll_layout.addWidget(label)
            scroll_layout.addWidget(input_field)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        submit_button = QPushButton('Submit and Get Diagnosis')
        submit_button.clicked.connect(self.submit_symptoms)
        layout.addWidget(submit_button)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        layout.addWidget(QLabel("Patient Diagnosis Summary:"))
        layout.addWidget(self.summary_display)

        self.setLayout(layout)

    def load_model(self):
        result = self.checker.load_model()
        self.result_display.setText(result)

    def unload_model(self):
        result = self.checker.unload_model()
        self.result_display.setText(result)

    def submit_symptoms(self):
        for key, input_field in self.inputs.items():
            self.checker.add_symptom(key, input_field.text())

        detailed_diagnosis, summary_diagnosis = self.checker.get_diagnosis_suggestion()
        self.display_symptoms_and_diagnosis(detailed_diagnosis, summary_diagnosis)

    def display_symptoms_and_diagnosis(self, detailed_diagnosis, summary_diagnosis):
        result = "Recorded Symptoms:\n\n"
        for key, value in self.checker.get_symptoms().items():
            if value:
                result += f"{key.replace('_', ' ').title()}: {value}\n"
        result += f"\nSuggested Diagnosis:\n{detailed_diagnosis}"
        self.result_display.setText(result)
        self.summary_display.setText(summary_diagnosis)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SymptomCheckerGUI()
    ex.show()
    sys.exit(app.exec())
