from agents import decentralised_agent


# Klasse voor producten
# Deze kan uitgebreid worden om complexere scenarios te simuleren
class Product(object):
    def __init__(self, name, weight=0, height=0, width=0, depth=0):
        self.name = name
        self.weight = weight
        self.volume = height * width * depth


# Klasse voor een loading dock
# Deze kan uitgebreid worden om complexere scenarios te simuleren
class Loading_Dock(object):
    def __init__(self, agent, position):
        self.agent: decentralised_agent.Decentralised_agent = agent
        self.position: (int, int) = position
        self.contents: list[Product] = []


# Klasse voor de positie, hiermee is het logische grid gevuld
# Deze kan uitgebreid worden om complexere scenarios te simuleren
class Position(object):
    def __init__(self):
        self.agent: decentralised_agent.Decentralised_agent | None = None
        self.loading_dock: Loading_Dock | None = None
        self.item: Product | None = None