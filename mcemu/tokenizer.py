from typing import List


class Token:
    def __init__(self, type: str, value: str, has_leading_space: bool = True):
        self.type = type
        self.value = value
        self.has_leading_space = has_leading_space

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def tokenize(self) -> List[Token]:
        tokens = []
        had_space = True
        while self.pos < len(self.text):
            char = self.text[self.pos]

            if char.isspace():
                self.pos += 1
                had_space = True
                continue

            if char in ('"', "'"):
                quote_type = char
                self.pos += 1
                start = self.pos
                while self.pos < len(self.text) and self.text[self.pos] != quote_type:
                    if self.text[self.pos] == "\\":
                        self.pos += 2
                    else:
                        self.pos += 1
                if self.pos >= len(self.text):
                    raise SyntaxError(f"Unterminated string literal (missing closing {quote_type!r})")
                val = self.text[start: self.pos]
                val = val.replace("\\" + quote_type, quote_type)
                tokens.append(Token("STRING", val, had_space))
                self.pos += 1
                had_space = False
                continue

            if char in "=+-*/%<>[]{},:.":
                op = char
                self.pos += 1

                if self.pos < len(self.text):
                    nxt = self.text[self.pos]
                    if op in ("+", "-", "*", "/", "%", "<", ">") and nxt == "=":
                        op += nxt
                        self.pos += 1
                    elif op == ">" and nxt == "<":
                        op += nxt
                        self.pos += 1
                    elif op == "." and nxt == ".":
                        op += nxt
                        self.pos += 1

                if op == "-" and self.pos < len(self.text) and self.text[self.pos].isdigit():
                    start = self.pos - 1
                    while self.pos < len(self.text) and (
                            self.text[self.pos].isalnum() or self.text[self.pos] in (".", "_")):
                        self.pos += 1
                    tokens.append(Token("WORD", self.text[start: self.pos], had_space))
                    had_space = False
                    continue

                tokens.append(
                    Token("PUNCT" if op in ("[", "]", "{", "}", ",", ":", ".", "..") else "OPERATOR", op, had_space))
                had_space = False
                continue

            start = self.pos
            while (self.pos < len(self.text) and not self.text[self.pos].isspace() and self.text[
                self.pos] not in "=+-*/%<>[]{},:"):

                if self.text[self.pos] == ".":
                    if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == ".":
                        break
                self.pos += 1

            word = self.text[start: self.pos]
            if word:
                tokens.append(Token("WORD", word, had_space))
                had_space = False
            else:
                self.pos += 1

        return tokens
