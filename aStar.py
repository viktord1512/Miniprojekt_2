
class Tærren:
    def __init__(self, navn, bevægelsesomkostning):
        self.navn = navn
        self.bevægelsesomkostning = bevægelsesomkostning

class Græs:
    def __init__(self):
        Tærren.__init__(self, "græs", 1)

class Vand:
     def __init__(self):
        Tærren.__init__(self, "vand", 2)

class Bjerg:
    def __init__(self):
        Tærren.__init__(self, "bjerg", 3)

class Lava:
    def __init__(self):
        Tærren.__init__(self, "Lava", None)