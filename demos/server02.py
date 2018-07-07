import asyncio
from typing import List
import json

import zmq
from dataclasses import dataclass
from zmq.asyncio import Context, Socket
from pymunk.vec2d import Vec2d

@dataclass
class Serializable:
    @classmethod
    def from_json(cls, data: str):
        d = json.loads(data)
        return cls(**d)

    def to_json(self) -> str:



@dataclass
class PlayerState(Serializable):
    position: Vec2d
    direction: Vec2d
    speed: float
    health: float
    ammo: float
    score: int


@dataclass
class GameState(Serializable):
    player_states: List[PlayerState]
    game_seconds: int



async def update_from_client():
    pass


async def send_game_state():
    pass


async def ticker():
    while True:




async def main():
    ctx = Context()
    try:
        asyncio.create_task(ticker())
        await asyncio.sleep(1000000)
    except asyncio.CancelledError:
        ctx.destroy(linger=1)


if __name__ == '__main__':
    asyncio.run(main())
