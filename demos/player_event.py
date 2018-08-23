from typing import Dict
from dataclasses import dataclass, asdict, field
from demos.movement import MOVE_MAP

@dataclass
class PlayerEvent:
    """
    p = PlayerEvent()
    p.keys[arcade.key.UP] = True
    """
    keys: Dict[int, bool] = field(
        default_factory=lambda: {k: False for k in MOVE_MAP}
    )

    def __post_init__(self):
        self.keys = {int(k): v for k, v in self.keys.items()}

    def asdict(self):
        return asdict(self)
