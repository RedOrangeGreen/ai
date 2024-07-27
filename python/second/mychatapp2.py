"""
LLM Chat Interface
Date Created: Saturday, July 27, 2024
Time Created: 10:00 AM

This script creates a graphical user interface (GUI) for interacting with a large language model (LLM)
using the tkinter library. Users can load a model, send messages, and receive responses. 
Features include:
- Copying chat text to the clipboard
- Clearing the chat text
- Context menu for the user input field
- Storing the last question and answer
- Menu options to display the last question and answer

Dependencies: tkinter, gpt4all
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu
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

        # New buttons for copy and clear
        self.copy_button = tk.Button(self.input_frame, text="Copy Chat", command=self.copy_chat)
        self.copy_button.pack(side=tk.RIGHT)

        self.clear_button = tk.Button(self.input_frame, text="Clear Chat", command=self.clear_chat)
        self.clear_button.pack(side=tk.RIGHT)

        # Context menu for user input
        self.user_input_menu = Menu(master, tearoff=0)
        self.user_input_menu.add_command(label="Copy", command=self.copy_input)
        self.user_input_menu.add_command(label="Paste", command=self.paste_input)

        self.user_input.bind("<Button-3>", self.show_context_menu)

        # Variables to store last question and answer
        self.last_question = ""
        self.last_answer = ""

        # Menu for last question and answer
        self.menu = Menu(master)
        master.config(menu=self.menu)
        file_menu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Last Question", command=self.show_last_question)
        file_menu.add_command(label="Last Answer", command=self.show_last_answer)

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
            self.last_question = user_message  # Store last question
            self.display_message("You: " + user_message)
            self.user_input.delete(0, tk.END)
            self.send_button.config(state=tk.DISABLED)

            def generate_response():
                try:
                    with self.model.chat_session():
                        response = self.model.generate(user_message, max_tokens=1024)
                        self.last_answer = response  # Store last answer
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

    def copy_chat(self):
        chat_content = self.chat_display.get("1.0", tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(chat_content.strip())

    def clear_chat(self):
        self.chat_display.config(state='normal')
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state='disabled')

    def show_context_menu(self, event):
        self.user_input_menu.post(event.x_root, event.y_root)

    def copy_input(self):
        input_text = self.user_input.get()
        self.master.clipboard_clear()
        self.master.clipboard_append(input_text)

    def paste_input(self):
        self.user_input.delete(0, tk.END)  # Clear current input
        self.user_input.insert(0, self.master.clipboard_get())  # Paste clipboard content

    def show_last_question(self):
        messagebox.showinfo("Last Question", self.last_question or "No question asked yet.")

    def show_last_answer(self):
        messagebox.showinfo("Last Answer", self.last_answer or "No answer generated yet.")

# Main application loop
root = tk.Tk()
app = LLMApp(root)
root.mainloop()