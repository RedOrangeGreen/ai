import tkinter as tk
from tkinter import scrolledtext
from gpt4all import GPT4All

class LLMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Question Interface")
        
        self.model = None
        
        # Create and place widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Model load button
        self.load_button = tk.Button(self.root, text="Load Model", command=self.load_model)
        self.load_button.pack(pady=10)
        
        # Question input
        self.question_label = tk.Label(self.root, text="Enter your question:")
        self.question_label.pack()
        
        self.question_entry = tk.Entry(self.root, width=50)
        self.question_entry.pack(pady=5)
        
        # Submit button
        self.submit_button = tk.Button(self.root, text="Submit", command=self.get_response)
        self.submit_button.pack(pady=10)
        
        # Response display
        self.response_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=20)
        self.response_text.pack(pady=10)
        
    def load_model(self):
        try:
            # Attempt to load the model with GPU acceleration
            self.model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf", device='gpu')
            self.response_text.insert(tk.END, "Model loaded successfully with GPU acceleration.\n")
        except Exception as e:
            # If GPU loading fails, fall back to CPU
            self.response_text.insert(tk.END, f"GPU loading failed: {str(e)}\nFalling back to CPU.\n")
            self.model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf", device='cpu')
            self.response_text.insert(tk.END, "Model loaded successfully on CPU.\n")
        
    def get_response(self):
        question = self.question_entry.get()
        if not self.model:
            self.response_text.insert(tk.END, "Please load the model first.\n")
            return
        
        with self.model.chat_session():
            response = self.model.generate(question, max_tokens=1024)
            self.response_text.insert(tk.END, f"Q: {question}\nA: {response}\n\n")

# Create the main window
root = tk.Tk()
app = LLMApp(root)
root.mainloop()
