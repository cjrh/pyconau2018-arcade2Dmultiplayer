import time
import asyncio
from asyncio import run, create_task, CancelledError
import zmq
from zmq.asyncio import Context, Socket
from pymunk.vec2d import Vec2d
from .lib02 import PlayerEvent, PlayerState, GameState
from .server_app import App
from demos.movement import KeysPressed, apply_movement


SERVER_UPDATE_TICK_HZ = 10


async def push_game_state(gs: GameState, sock: Socket):
    try:
        while True:
            await sock.send_string(gs.to_json())
            await asyncio.sleep(1 / SERVER_UPDATE_TICK_HZ)
    except asyncio.CancelledError:
        pass


async def update_from_client(gs: GameState, sock: Socket):
    try:
        while True:
            msg = await sock.recv_json()
            event_dict = msg['event']
            print(f'Got event dict: {event_dict}')
            event = PlayerEvent(**event_dict)
            update_game_state(gs, event)
    except asyncio.CancelledError:
        pass


def update_game_state(gs: GameState, event: PlayerEvent):
    player_state = gs.player_states[0]
    p = Vec2d(player_state.x, player_state.y)
    dt = time.time() - player_state.updated
    p = apply_movement(player_state.speed, dt, p, event)
    player_state.x, player_state.y = p.x, p.y
    player_state.updated = time.time()


async def main():
    fut = asyncio.Future()  # IGNORE!
    app = App(signal=fut)   # IGNORE!

    gs = GameState(player_states=[PlayerState(speed=150)])

    ctx = Context()

    sock1: Socket = ctx.socket(zmq.PUB)
    sock1.bind('tcp://*:25000')
    task1 = create_task(push_game_state(gs, sock1))

    sock2: Socket = ctx.socket(zmq.PULL)
    sock2.bind('tcp://*:25001')
    task2 = create_task(update_from_client(gs, sock2))

    try:
        await asyncio.wait([task1, task2, fut], return_when=asyncio.FIRST_COMPLETED)
    except CancelledError:
        print('Cancelled')
    finally:
        sock1.close(1)
        sock2.close(1)
        ctx.destroy(linger=1)


if __name__ == '__main__':
    run(main())
