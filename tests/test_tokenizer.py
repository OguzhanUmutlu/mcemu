from mcemu.tokenizer import Token, Tokenizer


def test_token_repr():
    t = Token("WORD", "hello")
    assert repr(t) == "Token(WORD, 'hello')"


def test_tokenizer_basic_words():
    tokenizer = Tokenizer("hello world")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 2
    assert tokens[0].type == "WORD"
    assert tokens[0].value == "hello"
    assert tokens[1].type == "WORD"
    assert tokens[1].value == "world"


def test_tokenizer_strings():
    tokenizer = Tokenizer("'hello world' \"test string\"")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 2
    assert tokens[0].type == "STRING"
    assert tokens[0].value == "hello world"
    assert tokens[1].type == "STRING"
    assert tokens[1].value == "test string"


def test_tokenizer_operators():
    tokenizer = Tokenizer("+= -= *= /= %= <= >=")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 7
    expected = ["+=", "-=", "*=", "/=", "%=", "<=", ">="]
    for i, exp in enumerate(expected):
        assert tokens[i].type == "OPERATOR"
        assert tokens[i].value == exp


def test_tokenizer_punctuation():
    tokenizer = Tokenizer("[,] {:} !@")
    tokens = tokenizer.tokenize()
    assert len(tokens) == 8
    expected = ["[", ",", "]", "{", ":", "}", "!", "@"]
    for i, exp in enumerate(expected):
        assert tokens[i].type == "PUNCT"
        assert tokens[i].value == exp
