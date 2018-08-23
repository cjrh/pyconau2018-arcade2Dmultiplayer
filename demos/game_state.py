from typing import List
import json
from dataclasses import dataclass, asdict


@dataclass
class PlayerState:
    updated: float = 0
    x: float = 0
    y: float = 0
    health: float = 0
    ammo: float = 0


@dataclass
class GameState:
    player_states: List[PlayerState]

    def to_json(self):
        d = dict(
            player_states=[asdict(p) for p in self.player_states],
        )
        return json.dumps(d)

    def from_json(self, data):
        d = json.loads(data)
        for i, p in enumerate(d['player_states']):
            self.player_states[i] = PlayerState(**p)
