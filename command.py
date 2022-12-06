import types

class Command:
    def __init__(self, name: str, onuse: types.FunctionType, help: str, minrank: int):
        self.name    = name
        self.onuse   = onuse
        self.help    = help
        self.minrank = minrank
