from typing import List
import json
from dataclasses import dataclass, asdict


@dataclass
class PlayerEvent:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False

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
