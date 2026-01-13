import random 
import tkinter as tk
from tkinter import ttk, messagebox
from pypdf import PdfReader

FILE_PATH = 'SAT1000.pdf'

def load_lines(path):
    """Load non-empty lines from SAT1000.pdf"""

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
        
    except FileNotFoundError:
        messagebox.showerror("File Not Found", f"Could not find: {path}")
        return []
    
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")
        return []
    
class VocabularyApp(tk.Tk):
    """Builds the application window"""
    def __init__(self, lines):
        super().__init__() #runs tk.TK's window initialization code first

        # window configuration
        self.title("SAT Vocabulary Practice")
        self.geometry("865x545")
        self.minsize(780, 495)

        # initialize attributes (instance variables)
        self.lines = lines
        self.current_word = ""
        self.current_definition = ""

        # create the user interface. Helper method for use inside the class
        self._build_ui()

        if not self.lines:
            # Disable controls if we have no data
            self.submit_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            self.next_word()

    def _build_ui(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # widgets styling
        style = ttk.Style()
        style.configure(
            "Word.TLabel",
            font=("Segoe UI", 16, "bold"),
            foreground="#1f4fd8"   # deep blue
        )
        style.configure(
            "AnswerLabel.TLabel", 
            font=("Segoe UI", 13, "bold")
        )
                
        # Title
        title = ttk.Label(container, text="SAT Vocabulary Practice", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        # Word display
        word_frame = ttk.Frame(container)
        word_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(word_frame, text="Word:", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.word_label = ttk.Label(word_frame, text="", style="Word.TLabel")
        self.word_label.pack(side="left", padx=(8, 0))

        # Student answer
        ttk.Label(container, text="Type the meaning (not graded):", style="AnswerLabel.TLabel").pack(anchor="w", pady=(6, 4))
        self.answer_entry = tk.Entry(container, font=("Segoe UI", 14))
        self.answer_entry.pack(fill="x", pady=(0, 10), ipady=6)

        # Buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=(18, 16))

        self.submit_btn = tk.Button(
                btn_frame, 
                text="Submit", 
                font=("Segoe UI", 13, "bold"), 
                bg="#1f4fd8",        # blue
                fg="white",
                activebackground="#173aa8",
                activeforeground="white",
                padx=14,
                pady=6,
                command=self.submit_answer
        )
        self.submit_btn.pack(side="left")

        self.next_btn = tk.Button(
            btn_frame,
            text="Next Word", 
            font=("Segoe UI", 13, "bold"),
            bg="#e0e0e0",        # neutral gray
            fg="black",
            activebackground="#cfcfcf",
            padx=14,
            pady=6, 
            command=self.next_word
        )
        self.next_btn.pack(side="left", padx=(12, 0))

        # Definition reveal
        ttk.Label(container, text="Correct meaning:", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(6, 4))
        self.definition_box = tk.Text(container, height=2, wrap="word")
        # Force font explicitly
        self.definition_box.configure(font=("Segoe UI", 14))
        self.definition_box.configure(
            bg="#f6f6f6",
            fg="#333333",
            relief="flat"
        )
        self.definition_box.configure(
            padx=6,
            pady=6
        )       
        self.definition_box.pack(fill="x", pady=(0, 10))
        self.definition_box.configure(state="disabled")

        # Allow pressing Enter to submit
        self.bind("<Return>", lambda event: self.submit_answer())

    def _set_definition_text(self, text):
            self.definition_box.configure(state="normal")
            self.definition_box.delete("1.0", "end")
            self.definition_box.insert("end", text)
            self.definition_box.configure(state="disabled")

    def next_word(self):
        line = random.choice(self.lines)
        word, definition = line.split(None, 1)

        # Your capitalization choice:
        word = word.capitalize()
        definition = definition.capitalize()

        self.current_word = word
        self.current_definition = definition

        self.word_label.configure(text=self.current_word)
        self.answer_entry.delete(0, "end")
        self._set_definition_text("")  # clear definition until submitted
        self.answer_entry.focus_set()

    def submit_answer(self):
        # No grading: reveal the correct definition
        self._set_definition_text(self.current_definition)




if __name__ == "__main__":
    lines = load_lines(FILE_PATH)
    app = VocabularyApp(lines)
    app.mainloop()
