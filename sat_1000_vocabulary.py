import random 
import tkinter as tk
from tkinter import ttk, messagebox
import re

FILE_PATH = 'SAT1000_cleaned.txt'

# some words have multiple definitions and sentence usages associated with them
SENSE_RE = re.compile(
    r"""
    \s*
    (?:(?P<num>\d+)\.\s*)?
    \((?P<pos>[^)]+)\)\s*
    (?P<definition>.*?)\s*
    \((?P<usage>[^)]+)\)
    """, re.VERBOSE
)

# part of speech mapping for display
POS_MAP = {
    "v.": "Verb",
    "n.": "Noun",
    "adj.": "Adjective",
    "adv.": "Adverb"
}


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

        # some words have multiple definitions
        self.current_senses = []
        self.current_sense_index = 0
        self.details_revealed = False
        
        # create the user interface. Helper method for use inside the class
        self._build_ui()

        if not self.all_lines:
            # Disable controls if we have no data
            self.submit_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            #self._update_counter()
            self.next_word()

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
            justify="left",
            anchor="w"
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

        # --- Sense navigation (hidden/disabled unless multiple senses) ---
        self.sense_frame = ttk.Frame(container)
        self.sense_frame.pack_forget()  # start hidden
        #sense_frame.pack(pady=(0, 6))

        self.sense_prev_btn = tk.Button(
            self.sense_frame,
            text="◀ Prev sense",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6f8",
            fg="#333333",
            activebackground="#e6e9ed",
            padx=10,
            pady=3,
            command=self.prev_sense
        )

        self.sense_prev_btn.pack(side="left")

        self.sense_label = ttk.Label(self.sense_frame, text="", style="FieldLabel.TLabel")
        self.sense_label.pack(side="left", padx=12)

        self.sense_next_btn = tk.Button(
            self.sense_frame,
            text="Next sense ▶",
            font=("Segoe UI", 10, "bold"),
            bg="#f4f6f8",
            fg="#333333",
            activebackground="#e6e9ed",
            padx=10,
            pady=3,
            command=self.next_sense
        )
        self.sense_next_btn.pack(side="left")
    
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

        # Counter at the VERY bottom-right
        self.counter_label = ttk.Label(bottom_bar, text="")
        self.counter_label.pack(side="bottom", anchor="e", padx=(0, 6), pady=(0, 2))

        # Buttons just above the counter
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
            command=self.show_details
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


        # Enter key triggers submit when enabled
        self.bind("<Return>", lambda event: self.submit_btn["state"] == "normal" and self.show_details())

    def next_word(self):
        if self.completed:
            self._reset_word_list()

        self._prepare_ui_for_new_word()
        self.details_revealed = False

        if not self.remaining_lines:
            self._reset_word_list()

        line = random.choice(self.remaining_lines)
        
        self.remaining_lines.remove(line)
        sense_dict = self._parse_vocab_line(line)
        word = sense_dict['word']
       
        # capitalization
        word = word.capitalize()
        self.current_word = word       
        self.word_label.configure(text=self.current_word)

        # some words have multiple definitions and sentence usages
        self.current_senses = sense_dict["senses"]  
        self.current_sense_index = 0
        
        
        self._set_sense_nav_visibility()
        self._update_sense_controls()

        self.submit_btn.configure(state="normal")
        self.next_btn.configure(state="disabled")  # enforce “Show Details first”
        
    def show_details(self):
        # Count this as "attempted" and update UI
        self.words_attempted += 1
        self._update_counter()

        self.details_revealed = True
        self._render_current_sense()
        self._set_sense_nav_visibility()

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

    def _set_sense_nav_visibility(self):
        """Show sense navigation only when multiple senses exist."""
        total = len(self.current_senses) if self.current_senses else 0

        if total > 1:
            self.sense_frame.pack(pady=(0, 6))
        else:
            self.sense_frame.pack_forget()


    def _render_current_sense(self):
        if not self.current_senses:
            self._prepare_ui_for_new_word()
            return
        
        # get the appropriate list item (which is a dictionary) for display
        s = self.current_senses[self.current_sense_index]

        # for display, don't abbreviate the part of speech
        raw_pos = s.get("pos", "").lower()
        display_pos = POS_MAP.get(raw_pos, raw_pos.rstrip(".").capitalize())
        self.pos_value.configure(text=display_pos)

        self.def_value.configure(text=s['definition'].capitalize())
        
        self.usage_value.configure(
            text=self._capitalize_sentence(s['usage'])
        )

        self._update_sense_controls()

    def next_sense(self):
        # Navigation only works after sense details have been displayed
        if not self.details_revealed:
            return
        if self.current_sense_index < len(self.current_senses) - 1:
            self.current_sense_index += 1
            self._render_current_sense()

    def prev_sense(self):
        # Navigation only works after sense details have been displayed
        if not self.details_revealed:
            return
        if self.current_sense_index > 0:
            self.current_sense_index -= 1
            self._render_current_sense()

    def _update_sense_controls(self):
        total = len(self.current_senses)

        if total <=1 or not self.details_revealed:
            self.sense_label.configure(text="")
            self.sense_prev_btn.configure(state="disabled")
            self.sense_next_btn.configure(state="disabled")
            self.sense_frame.pack_forget()
            return
        
        # Show the frame 
        self.sense_frame.pack(pady=(0, 6))
        
        # show "Sense 1/2" etc
        self.sense_label.configure(text=f"Sense {self.current_sense_index + 1}/{total}")
        # enable/disable
        self.sense_prev_btn.configure(state=("normal" if self.current_sense_index > 0 else "disabled"))
        self.sense_next_btn.configure(state=("normal" if self.current_sense_index < total - 1 else "disabled"))

    def _update_counter(self):
        self.counter_label.configure(
            text=f"{self.words_attempted} of {self.total_words} words answered"
        )

    def _parse_vocab_line(self, line:str) -> dict:
        # removing leading and ending spaces, single quotes, and double quotes
        line = line.strip().strip("'").strip('"')

        line_parts = line.split(None, 1)
        if len(line_parts) != 2:
            raise ValueError(f"Bad line (no remainder after word): {line!r}")
        
        word = line_parts[0]
        rest_of_line = line_parts[1] #POS, definition, sentence usage

        # some words have multiple 'senses': 2 or more definitions
        senses = []
        for match in SENSE_RE.finditer(rest_of_line):
            num = match.group("num")
            senses.append({
                "num": int(num) if num else None,   
                "pos": match.group("pos").strip(),
                "definition": " ".join(match.group("definition").split()),
                "usage": " ".join(match.group("usage").split())
            })

        if not senses:
            raise ValueError(f"Bad line (no senses parsed): {line!r}")
        
        return {'word' : word, 'senses' : senses}
    
    def _prepare_ui_for_new_word(self):
    # Clear the window and disable the sense buttons
        self.pos_value.configure(text="")
        self.def_value.configure(text="")
        self.usage_value.configure(text="")
        self.sense_label.configure(text="")
        self.sense_prev_btn.configure(state="disabled")
        self.sense_next_btn.configure(state="disabled")

        # Always hide sense navigation for a new word
        self.sense_frame.pack_forget()

        self._update_counter()

    def _capitalize_sentence(self, text):
        '''Capitalizes the first alphabetic character in a sentence'''
        for i, ch in enumerate(text):
            if ch.isalpha():
                return text[:i] + ch.upper() + text[i+1:]
        return text

    def _reset_word_list(self):
        self.remaining_lines = self.all_lines[:]
        self.words_attempted = 0
        self.completed = False
        self.next_btn.configure(text="Next Word")


if __name__ == "__main__":
    text = load_lines(FILE_PATH)
    app = AdvancedVocabularyApp(text)
    app.mainloop()
