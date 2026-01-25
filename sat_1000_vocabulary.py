import random 
import tkinter as tk
from tkinter import ttk, messagebox


FILE_PATH = 'SAT1000_cleaned.txt'

def load_lines(path):
    """Load non-empty lines from SAT1000_cleaned.txt"""

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
        
    except FileNotFoundError:
        messagebox.showerror("File Not Found", f"Could not find: {path}")
        return []
    
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")
        return []
        
class AdvancedVocabularyApp(tk.Tk):
    """Builds the application window"""
    def __init__(self, lines):
        super().__init__() #runs tk.TK's window initialization code first

        # window configuration
        self.title("SAT Advanced Vocabulary Practice")
        self.geometry("865x545")
        self.minsize(780, 495)

        # initialize attributes (instance variables)
        self.all_lines = lines[:] # immutable list of words
        self.remaining_lines = lines[:] # mutable list of words (word removed after it is reviewed)
        self.current_word = ""
        self.current_part_of_speech = ""
        self.current_definition = ""
        self.current_sentence_usage = ""
        self.words_attempted = 0
        self.total_words = len(self.all_lines)
        self.completed = False # will be set to True after all words reviewed
        
        # create the user interface. Helper method for use inside the class
        self._build_ui()

        if not self.all_lines:
            # Disable controls if we have no data
            self.submit_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        #else:
            #self._update_counter()
            #self.next_word()

    def _build_ui(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # --- Styling ---
        style = ttk.Style()
        style.configure(
            "Word.TLabel",
            font=("Segoe UI", 30, "bold"),
            foreground="#1f4fd8"   # deep blue
        )
        style.configure(
            "FieldLabel.TLabel",
            font=("Segoe UI", 11, "bold"),
            foreground="#2c3e50"
        )
        style.configure(
            "FieldValue.TLabel",
            font=("Segoe UI", 13),
            foreground="#2c3e50",
            wraplength=720,
            justify="center"
        )
                       
        # --- Title ---
        title = ttk.Label(
        container,
        text="SAT Advanced Vocabulary Practice",
        font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=(0, 20))

        # --- Word display ---
        word_frame = ttk.Frame(container)
        word_frame.pack(pady=(0, 10))

        self.word_label = ttk.Label(word_frame, text="", style="Word.TLabel")
        self.word_label.pack()
    
        # --- Revealed fields (start blank; populated on submit) ---
        info_frame = ttk.Frame(container)
        info_frame.pack(fill="x", pady=(10, 0))

        left_block = ttk.Frame(info_frame, padding=(40, 0, 0, 0))  # 40px left indent
        left_block.pack(fill="x", anchor="w")

        # Part of speech
        ttk.Label(left_block, text="Part of speech:", style="FieldLabel.TLabel").pack(anchor="w", pady=(8, 2))
        self.pos_value = ttk.Label(left_block, text="", style="FieldValue.TLabel")
        self.pos_value.pack(anchor="w")

        # Definition
        ttk.Label(left_block, text="Definition:", style="FieldLabel.TLabel").pack(anchor="w", pady=(12, 2))
        self.def_value = ttk.Label(left_block, text="", style="FieldValue.TLabel")
        self.def_value.pack(anchor="w")

        # Sentence usage
        ttk.Label(left_block, text="Sentence usage:", style="FieldLabel.TLabel").pack(anchor="w", pady=(12, 2))
        self.usage_value = ttk.Label(left_block, text="", style="FieldValue.TLabel")
        self.usage_value.pack(anchor="w")

        # Spacer so the bottom bar doesn't crowd the content
        ttk.Frame(container).pack(fill="both", expand=True)

        # --- Bottom bar: buttons + counter ---
        bottom_bar = ttk.Frame(container)
        bottom_bar.pack(side="bottom", fill="x", pady=(12, 0))

        # Buttons centered in their own frame
        btn_frame = ttk.Frame(bottom_bar)
        btn_frame.pack(side="bottom", pady=(0, 6))        

        self.submit_btn = tk.Button(
            btn_frame,
            text="Show Details",
            font=("Segoe UI", 13, "bold"),
            bg="#1f4fd8",
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
            bg="#f4f6f8",
            fg="#333333",
            activebackground="#e6e9ed",
            padx=14,
            pady=6,
            command=self.next_word
        )
        self.next_btn.pack(side="left", padx=(18, 0))

        # Status/counter on the bottom right (same bar)
        self.counter_label = ttk.Label(bottom_bar, text="")
        self.counter_label.pack(side="right")

        # Enter key triggers submit when enabled
        self.bind("<Return>", lambda event: self.submit_btn["state"] == "normal" and self.submit_answer())

    def next_word(self):
        if self.completed:
            self._reset_word_list()

        self._prepare_ui_for_new_word()

        if not self.remaining_lines:
            self._reset_deck()

        line = random.choice(self.remaining_lines)
        self.remaining_lines.remove(line)
        word, definition = line.split(None, 1)

        # Your capitalization choice:
        word = word.capitalize()
        definition = definition.capitalize()

        self.current_word = word
        self.current_definition = definition

        self.word_label.configure(text=self.current_word)
        self.answer_entry.delete(0, "end")
        #self._set_definition_text("")  # clear definition until submitted
        self.answer_entry.focus_set()

    def submit_answer(self):
        # No grading: reveal the correct definition
        self._set_definition_text(self.current_definition)

        # Count this as "attempted" and update UI
        self.words_attempted += 1
        self._update_counter()

        # disable the submit button after clicking it and enable the next word button
        self.submit_btn.configure(state="disabled")
        self.next_btn.configure(state="normal")

        # If that was the last word, notify and reset on next "Next Word"
        if len(self.remaining_lines) == 0:
            messagebox.showinfo(
                "All Done",
                "Congratulations! You have reviewed all the words.\n\n"
                "Clicking 'Next Word' will reset the word list and your progress."
                )
            self.completed = True
            self.next_btn.configure(text="Restart")

    def _update_counter(self):
        self.counter_label.configure(
            text=f"{self.words_attempted} words answered out of {self.total_words}"
        )

    def _prepare_ui_for_new_word(self):
    # Clear definition and re-enable submit button for a new attempt
        self._set_definition_text("")
        self.submit_btn.configure(state="normal")
        self.next_btn.configure(state="disabled")
        self._update_counter()

    def _reset_word_list(self):
        self.remaining_lines = self.all_lines[:]
        self.words_attempted = 0
        self.completed = False
        self.next_btn.configure(text="Next Word")


if __name__ == "__main__":
    text = load_lines(FILE_PATH)
    app = AdvancedVocabularyApp(text)
    app.mainloop()
