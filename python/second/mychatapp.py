import tkinter as tk
from tkinter import scrolledtext
from gpt4all import GPT4All
import threading

class LLMApp:
    def __init__(self, master):
        self.master = master
        master.title("LLM Chat Interface")

        # Model loading section
        self.load_frame = tk.Frame(master)
        self.load_frame.pack(pady=10)

        self.load_button = tk.Button(self.load_frame, text="Load Model", command=self.load_model)
        self.load_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(self.load_frame, text="Model not loaded")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Chat interface
        self.chat_frame = tk.Frame(master)
        self.chat_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, state='disabled', height=20)
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        self.input_frame = tk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.user_input = tk.Entry(self.input_frame, width=50)
        self.user_input.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.user_input.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        self.model = None
        self.lock = threading.Lock()

    def load_model(self):
        def load():
            self.status_label.config(text="Loading model...")
            try:
                self.model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
                self.status_label.config(text="Model loaded")
                self.load_button.config(state=tk.DISABLED)
            except Exception as e:
                self.status_label.config(text=f"Error loading model: {str(e)}")

        threading.Thread(target=load).start()

    def send_message(self, event=None):
        user_message = self.user_input.get().strip()
        if user_message and self.model:
            self.display_message("You: " + user_message)
            self.user_input.delete(0, tk.END)
            self.send_button.config(state=tk.DISABLED)

            def generate_response():
                try:
                    with self.model.chat_session():
                        response = self.model.generate(user_message, max_tokens=1024)
                    self.display_message("AI: " + response)
                except Exception as e:
                    self.display_message(f"Error: {str(e)}")
                finally:
                    self.send_button.config(state=tk.NORMAL)

            threading.Thread(target=generate_response).start()
        elif not self.model:
            self.display_message("System: Please load the model first.")

    def display_message(self, message):
        with self.lock:
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, message + "\n\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state='disabled')

root = tk.Tk()
app = LLMApp(root)
root.mainloop()
