class CommandReturn(Exception):
    def __init__(self, value: int):
        self.value = value
