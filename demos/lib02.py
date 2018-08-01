from typing import List, Dict
import json
from dataclasses import dataclass, asdict, field
from arcade import key
from demos.movement import KEYS


@dataclass
class PlayerEvent:
    keys: Dict = field(default_factory=lambda: {k: False for k in KEYS})

    def __post_init__(self):
        self.keys = {int(k): v for k, v in self.keys.items()}

    def asdict(self):
        return asdict(self)


@dataclass
class PlayerState:
    updated: float = 0
    x: float = 0
    y: float = 0
    speed: float = 0
    health: float = 0
    ammo: float = 0
    score: int = 0

    def asdict(self):
        return asdict(self)


@dataclass
class GameState:
    player_states: List[PlayerState]
    game_seconds: int

    def to_json(self):
        d = dict(
            player_states=[asdict(p) for p in self.player_states],
            game_seconds=self.game_seconds
        )
        return json.dumps(d)

    def from_json(self, data):
        d = json.loads(data)
        self.game_seconds = d['game_seconds']
        for i, p in enumerate(d['player_states']):
            self.player_states[i] = PlayerState(**p)


if __name__ == '__main__':
    pe = PlayerEvent()
    print(pe)
    print(pe.asdict())
    assert pe.asdict() == {'keys': {65362: False, 65364: False, 65361: False, 65363: False}}
