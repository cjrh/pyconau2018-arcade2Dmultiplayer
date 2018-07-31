from dataclasses import dataclass, fields
from typing import List, Dict


@dataclass(init=False)
class BitField:
    _value: int = 0

    def testBit(self, offset):
        mask = 1 << offset
        return self._value & mask

    def setBit(self, offset):
        # setBit() returns an integer with the bit at 'offset' set to 1.
        mask = 1 << offset
        return self._value | mask

    def clearBit(self, offset):
        # clearBit() returns an integer with the bit at 'offset' cleared.
        mask = ~(1 << offset)
        return self._value & mask

    def toggleBit(self, offset):
        # toggleBit() returns an integer with the bit at 'offset' inverted,
        # 0 -> 1 and 1 -> 0.
        mask = 1 << offset
        return self._value ^ mask

    def as_int(self):
        cs = ['1' if getattr(self, f.name) else '0' for f in fields(self)]
        return int(''.join(cs), 2)

    @classmethod
    def from_int(cls, value):
        flds = fields(cls)
        count = len(flds)
        inst = cls()
        for f, c in zip(flds, ('{:0%sb}' % count).format(value)):
            setattr(inst, f.name, c == '1')
        return inst


if __name__ == '__main__':
    @dataclass
    class Movement(BitField):
        left: bool = False
        right: bool = False
        up: bool = False
        down: bool = False

    m = Movement()
    print(m.as_int())
    m.right = True
    print(m.as_int())
    m.down = True
    print(m.as_int())

    x = m.as_int()
    m2 = Movement.from_int(x)
    print(m2.as_int())
    print(m2)

