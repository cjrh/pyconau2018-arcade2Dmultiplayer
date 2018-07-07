import json
import dataclasses
from dataclasses import dataclass
from pymunk.vec2d import Vec2d






@dataclass
class A:
    x: int
    y: float
    z: Vec2d

    class Encoder(json.JSONEncoder):
        def default(self, o):
            d = dataclasses.asdict(o)
            for f in dataclasses.fields(o):
                if f.type is Vec2d:
                    d[f.name] = tuple(d[f.name])
            return d

    @classmethod
    def decode_object_hook(cls, d):
        for f in dataclasses.fields(cls):
            if f.type is Vec2d:
                d[f.name] = Vec2d(*d[f.name])
        return cls(**d)


def test():
    a = A(1, 2.0, Vec2d.zero())
    s = json.dumps(a, cls=A.Encoder)
    print(s)

    aa = json.loads(s, object_hook=A.decode_object_hook)
    print(aa)


if __name__ == '__main__':
    test()
