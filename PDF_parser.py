"""This module takes a PDF file that has been converted to a text file as input and returns a
cleaned text file. White space, form feeds, and noise words are removed."""

import re
from pathlib import Path

IN_PATH = Path("SAT1000.txt")
OUT_PATH = Path("SAT1000_cleaned.txt")

# line starts with a word (^[A-Za-z][A-Za-z-]*), at least one space(\s+), optional number ((?:\d+\.\s+)?), 
# part of speech (\([A-Za-z]+\.\)), at least one space (\s+)
ENTRY_START_RE = re.compile(
    r"^[^\W\d_][^\s()]*\s+(?:\d+\.\s*)?\([A-Za-z]+\.?\)\s*",
    re.UNICODE,
)

ENTRY_START_ANYWHERE_RE = re.compile(
    r"\b[^\W\d_][^\s()]*\s+(?:\d+\.\s*)?\([A-Za-z]+\.?\)\s*",
    re.UNICODE,
)

HEADWORD_ALONE_RE = re.compile(r"^[A-Za-z][A-Za-z-]*$")
POS_LINE_RE = re.compile(r"^(?:\d+\.\s*)?\([A-Za-z]+\.?\)\s*")


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

def build_lines(raw_lines: list[str]) -> list[str]:
    """rstrip each raw line; if a line contains multiple entry-starts, split it."""
    out: list[str] = []

    for ln in raw_lines:
        ln = ln.rstrip()
        matches = list(ENTRY_START_ANYWHERE_RE.finditer(ln))

        if len(matches) <= 1:
            out.append(ln)
            continue

        # Rare in your current pdftotext output, but safe to keep.
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(ln)
            out.append(ln[start:end].strip())

    return out

def stitch_headword_pos(lines: list[str]) -> list[str]:
    """
    If a headword appears alone on one line and the next non-noise line starts with a POS,
    combine them into one synthetic entry-start line: 'buttress' + '(n.) ...' => 'buttress (n.) ...'
    """
    stitched: list[str] = []
    i = 0

    while i < len(lines):
        ln = lines[i].strip()

        if is_noise_line(ln):
            i += 1
            continue

        if HEADWORD_ALONE_RE.match(ln):
            j = i + 1
            while j < len(lines) and is_noise_line(lines[j]):
                j += 1

            if j < len(lines):
                nxt = lines[j].strip()
                if POS_LINE_RE.match(nxt):
                    stitched.append(f"{ln} {nxt}".strip())
                    i = j + 1
                    continue

        stitched.append(lines[i])
        i += 1

    return stitched

def assemble_entries(lines: list[str]) -> list[str]:
    """Your existing start/continuation logic, unchanged."""
    entries: list[str] = []
    current: list[str] = []

    for ln in lines:
        if is_noise_line(ln):
            continue

        s = ln.strip()
        if ENTRY_START_RE.match(s):
            if current:
                entries.append(normalize_whitespace(" ".join(current)))
            current = [s]
        else:
            if current:
                current.append(s)

    if current:
        entries.append(normalize_whitespace(" ".join(current)))

    return entries

def parse_entries(text: str) -> list[str]:
    text = text.replace("\f", "\n")
    raw_lines = text.splitlines()

    lines = build_lines(raw_lines)
    lines = stitch_headword_pos(lines)   

    entries = assemble_entries(lines)

    return entries

def main() -> None:
    text = IN_PATH.read_text(encoding="utf-8", errors="replace")
    entries = parse_entries(text)

    OUT_PATH.write_text("\n".join(entries) + "\n", encoding="utf-8")

    
if __name__ == "__main__":
    main()