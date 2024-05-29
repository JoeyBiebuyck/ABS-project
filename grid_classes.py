class Product(object):
    def __init__(self, name, weight=0, height=0, width=0, depth=0):
        self.name = name
        self.weight = weight
        self.volume = height * width * depth

class Loading_Dock(object):
    def __init__(self, agent, position):
        self.agent = agent
        self.position = position
        self.contents = []

class Position(object):
    def __init__(self):
        self.agent = None
        self.loading_dock = None
        self.item = None