import tkinter as tk
import subprocess
import threading

class ClipboardMonitor:
    def __init__(self, master):
        self.master = master
        master.title("Clipboard Monitor")

        self.status_label = tk.Label(master, text="", font=("Arial", 24))
        self.status_label.pack(pady=20)

        self.clear_button = tk.Button(master, text="Clear Clipboard", command=self.clear_clipboard)
        self.clear_button.pack(pady=10)

        self.running = True
        self.check_thread = threading.Thread(target=self.check_clipboard)
        self.check_thread.start()

    def check_clipboard(self):
        while self.running:
            clipboard_content = self.get_clipboard_content()
            if clipboard_content.strip():
                self.status_label.config(text="FULL", fg="red")
            else:
                self.status_label.config(text="EMPTY", fg="green")
            self.master.after(500, self.check_clipboard)
            break  # Exit the while loop as we're using after() for periodic checks

    def get_clipboard_content(self):
        try:
            return subprocess.check_output(['xclip', '-o', '-selection', 'clipboard'], universal_newlines=True)
        except subprocess.CalledProcessError:
            return ""

    def clear_clipboard(self):
        subprocess.run(['xclip', '-selection', 'clipboard', '-i'], input="", text=True)

    def on_closing(self):
        self.running = False
        self.master.destroy()

root = tk.Tk()
app = ClipboardMonitor(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
