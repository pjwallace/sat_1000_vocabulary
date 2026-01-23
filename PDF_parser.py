"""This module takes a PDF file that has been converted to a text file as input and returns a
cleaned text file. White space, form feeds, and noise words are removed."""

import re
from pathlib import Path

IN_PATH = Path("SAT1000.txt")
OUT_PATH = Path("SAT1000_clean_entries.txt")

# line starts with a word (^[A-Za-z][A-Za-z-]*), at least one space(\s+), optional number ((?:\d+\.\s+)?), 
# part of speech (\([A-Za-z]+\.\)), at least one space (\s+)
ENTRY_START_RE = re.compile(
    r"^[A-Za-z][A-Za-z-]*\s+(?:\d+\.\s+)?\([A-Za-z]+\.\)\s+"
)

# PDF text to eliminate from the file
NOISE_EXACT = {
    "SAT Vocabulary",
    "The 1000 Most",
    "Common SAT",
    "Words",
}

def is_section_letter(line:str) -> bool:
    """ The PDF is in alphabetical order. Each section is demarcated by a capital letter"""
    s = line.strip()
    return len(s) == 1 and s.isalpha() and s.isupper()

def is_noise_line(line:str) -> bool:
    """Check whether the line is blank, a noise line, or a section header. Return True is so."""
    s = line.strip()

    if not s:
        return True
    
    if s in NOISE_EXACT:
        return True
    
    if is_section_letter(s):
        return True
    
    return False

def normalize_whitespace(s: str) -> str:
    return " ".join(s.split())

def parse_entries(text: str) -> list[str]:
    # Normalize form feeds to newlines, then split
    text = text.replace("\f", "\n")
    raw_lines = text.splitlines()

    # Clean lines (strip right side; keep left since entry-start uses ^)
    lines = [ln.rstrip() for ln in raw_lines]

    entries: list[str] = [] # holds the final output: one string per vocabulary word
    current: list[str] = [] # holds each line until a new word is reached. These lines will be
                            # assembled into the final string

    for ln in lines:
        if is_noise_line(ln):
            continue

        # new word entry 
        if ENTRY_START_RE.match(ln.strip()):
            # close previous entry
            if current:
                entries.append(normalize_whitespace(" ".join(current)))
            current = [ln.strip()] # first line of the new entry
        else:
            # continuation line
            if current:
                current.append(ln.strip())

    # handles the last entry
    if current:
        entries.append(normalize_whitespace(" ".join(current)))

    return entries

def main() -> None:
    text = IN_PATH.read_text(encoding="utf-8", errors="replace")
    entries = parse_entries(text)
    OUT_PATH.write_text("\n".join(entries) + "\n", encoding="utf-8")

    print(f"Input:  {IN_PATH.resolve()}")
    print(f"Output: {OUT_PATH.resolve()}")
    print(f"Entries: {len(entries)}")
    print("First 10 entries:")
    for e in entries[:10]:
        print("-", e)

if __name__ == "__main__":
    main()