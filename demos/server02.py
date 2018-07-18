import asyncio
import time
from asyncio import run, create_task, CancelledError
from typing import List
import json

import zmq
import dataclasses
from dataclasses import dataclass, asdict
from zmq.asyncio import Context, Socket
from pymunk.vec2d import Vec2d


@dataclass
class PlayerEvent:
    left: bool
    right: bool
    up: bool
    down: bool


@dataclass
class PlayerState:
    updated: float = 0
    x: float = 0
    y: float = 0
    speed: float = 0
    health: float = 0
    ammo: float = 0
    score: int = 0


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


def update_game_state(gs: GameState, event: PlayerEvent):
    """This is the main engine of the game"""
    # TODO: look up player index
    player_state = gs.player_states[0]

    dt = time.time() - player_state.updated

    if event.left:
        player_state.x -= player_state.speed * dt

    if event.right:
        player_state.x += player_state.speed * dt

    if event.up:
        player_state.y += player_state.speed * dt

    if event.down:
        player_state.y -= player_state.speed * dt

    # Constraints
    if player_state.x < 0:
        player_state.x = 0
    if player_state.x > 800:
        player_state.x = 800

    if player_state.y < 0:
        player_state.y = 0
    if player_state.y > 600:
        player_state.y = 600

    # Mark the timestamp on this player's state
    player_state.updated = time.time()


async def update_from_client(gs: GameState, sock: Socket):
    while True:
        event = await sock.recv_string()
        update_game_state(gs, event)


async def ticker(sock1, sock2):
    ps = PlayerState()
    gs = GameState(player_states=[ps], game_seconds=1)
    s = gs.to_json()
    print(s)

    create_task(update_from_client(gs, sock2))

    # Send out the game state regularly
    tick_rate_Hz = 60
    while True:
        await sock1.send_string(gs.to_json())
        await asyncio.sleep(1 / tick_rate_Hz)


async def main():
    ctx = Context()

    sock_push_gamestate: Socket = ctx.socket(zmq.PUB)
    sock_push_gamestate.bind('tcp://*:25000')

    sock_recv_player_evts: Socket = ctx.socket(zmq.PULL)
    sock_recv_player_evts.bind('tcp://*:25001')

    try:
        create_task(ticker(sock_push_gamestate, sock_recv_player_evts))
        await asyncio.sleep(1000000)
    except CancelledError:
        print('Cancelled')
    finally:
        sock_push_gamestate.close(1)
        sock_recv_player_evts.close(1)
        ctx.destroy(linger=1)


if __name__ == '__main__':
    run(main())
