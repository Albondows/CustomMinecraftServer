import tomllib

class Rank:
    def __init__(self, num, name, color, max_draw, max_maps):
        self.num = num
        self.name = name
        self.color = color
        self.max_draw = max_draw
        self.max_maps = max_maps
    
    def __repr__(self):
        return 'Rank(%d, %s, %s, %d, %d)' % (self.num, self.name, self.color, self.max_draw, self.max_maps)

def load(fp):
    with open(fp, 'rb') as f:
        cfg = tomllib.load(f)

    return {v["rank"]: Rank(v["rank"], v["name"], v["color"], v["max_draw"], v["max_maps"]) for k, v in cfg.items() if isinstance(v, dict)}
