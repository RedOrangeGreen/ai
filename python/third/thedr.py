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
Show me a python application to ask these questions one after the other and store the symptoms
Add a PyQt6 wrapper
Add code to create a single question which is passed into the GPT4All SDK to ask for a suggested diagnosis given all the symptoms. Use the "Phi-3-mini-4k-instruct.Q4_0.gguf" LLM model (exact case as shown)
Enhance with buttons to load and unload the LLM model
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
import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QMessageBox, QDialog
from PyQt6.QtCore import Qt
from gpt4all import GPT4All

class DiagnosisSummaryDialog(QDialog):
    def __init__(self, symptoms, diagnosis, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patient Diagnosis Summary")
        self.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout()
        
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        
        # Construct the summary
        summary = "Patient Diagnosis Summary\n\n"
        summary += "Symptoms:\n"
        for key, value in symptoms.items():
            if key != "timestamp":
                summary += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        summary += "\nSuggested Diagnosis:\n"
        summary += diagnosis
        
        summary_text.setPlainText(summary)
        layout.addWidget(summary_text)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class SymptomChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.questions = [
            "What is your main symptom?",
            "When did your symptoms start?",
            "Are the symptoms constant or do they come and go?",
            "Are the symptoms getting better, worse, or staying the same?",
            "Does anything seem to make your symptoms worse?",
            "Does anything make your symptoms better?",
            "Have you tried any treatments or remedies so far? If so, which ones?",
            "How are these symptoms affecting your daily activities?",
            "Have you experienced any recent changes in your life or health?",
            "Are you taking any medications, including over-the-counter drugs or supplements?",
            "Do you have any known allergies or medical conditions?",
            "Have you ever experienced similar symptoms before?",
            "Does anyone in your family have a history of similar issues?",
            "What is your diet like?",
            "How much sleep are you getting?",
            "What is your stress level like?"
        ]
        self.current_question = 0
        self.symptoms = {}
        self.model = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Symptom Checker')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Add buttons for loading and unloading the model
        button_layout = QHBoxLayout()
        self.load_model_button = QPushButton('Load LLM Model')
        self.load_model_button.clicked.connect(self.load_model)
        button_layout.addWidget(self.load_model_button)

        self.unload_model_button = QPushButton('Unload LLM Model')
        self.unload_model_button.clicked.connect(self.unload_model)
        self.unload_model_button.setEnabled(False)
        button_layout.addWidget(self.unload_model_button)

        layout.addLayout(button_layout)

        self.question_label = QLabel(self.questions[self.current_question])
        layout.addWidget(self.question_label)

        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_input)

        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_question)
        layout.addWidget(self.next_button)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.result_text)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def load_model(self):
        try:
            self.model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
            self.load_model_button.setEnabled(False)
            self.unload_model_button.setEnabled(True)
            QMessageBox.information(self, "Model Loaded", "LLM model has been loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load the model: {str(e)}")

    def unload_model(self):
        if self.model:
            del self.model
            self.model = None
            self.load_model_button.setEnabled(True)
            self.unload_model_button.setEnabled(False)
            QMessageBox.information(self, "Model Unloaded", "LLM model has been unloaded.")

    def next_question(self):
        answer = self.answer_input.text().strip()
        if answer:
            question_key = self.questions[self.current_question].lower().replace(" ", "_").replace("?", "")
            self.symptoms[question_key] = answer
            self.current_question += 1
            self.answer_input.clear()

            if self.current_question < len(self.questions):
                self.question_label.setText(self.questions[self.current_question])
            else:
                self.finish_questionnaire()

    def finish_questionnaire(self):
        self.symptoms["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result = "Symptom Information Collected:\n\n"
        for key, value in self.symptoms.items():
            result += f"{key.replace('_', ' ').title()}: {value}\n"

        self.result_text.setText(result)
        self.question_label.setText("Questionnaire Completed")
        self.answer_input.setEnabled(False)
        self.next_button.setEnabled(False)

        # Save to file
        with open("symptoms_record.txt", "w") as file:
            file.write(result)

        # Get diagnosis suggestion if model is loaded
        if self.model:
            diagnosis = self.get_diagnosis_suggestion()
            self.result_text.append("\n\nSuggested Diagnosis:\n" + diagnosis)
            
            # Show the diagnosis summary dialog
            summary_dialog = DiagnosisSummaryDialog(self.symptoms, diagnosis, self)
            summary_dialog.exec()
        else:
            self.result_text.append("\n\nNote: LLM model is not loaded. Load the model to get a diagnosis suggestion.")

    def get_diagnosis_suggestion(self):
        symptoms_list = [f"{key.replace('_', ' ')}: {value}" for key, value in self.symptoms.items() if key != "timestamp"]
        prompt = f"""Given the following symptoms:
{', '.join(symptoms_list)}

What is a possible diagnosis? Provide a brief explanation for your suggestion."""

        with self.model.chat_session():
            response = self.model.generate(prompt, max_tokens=200)
        
        return response.strip()

def main():
    app = QApplication(sys.argv)
    ex = SymptomChecker()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
