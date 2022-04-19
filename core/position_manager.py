class Position():
    def __init__(self, idx, col, ln, filename, text):
        self.idx = idx
        self.col = col
        self.ln = ln
        self.filename = filename
        self.text = text
    
    def __repr__(self) -> str:
        return f"In {self.filename}, line {self.ln}, column {self.col}"

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        if current_char == "\n":
            self.ln += 1
            self.col = 1
        return self
    
    def copy(self):
        return Position(self.idx, self.col, self.ln, self.filename, self.text)
