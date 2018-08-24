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


async def update_from_client(gs: GameState, sock: Socket):
    """ TASK B """
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
    for ps in gs.player_states:
        p = Vec2d(ps.x, ps.y)
        dt = time.time() - ps.updated
        p = apply_movement(ps.speed, dt, p, event)
        ps.x, ps.y = p.x, p.y
        ps.updated = time.time()

async def push_game_state(gs: GameState, sock: Socket):
    """ TASK C """
    try:
        while True:
            await sock.send_string(gs.to_json())
            await asyncio.sleep(1 / SERVER_UPDATE_TICK_HZ)
    except asyncio.CancelledError:
        pass

async def main():
    fut = asyncio.Future()  # IGNORE!
    app = App(signal=fut)   # IGNORE!

    gs = GameState(player_states=[PlayerState(speed=150)])

    ctx = Context()  # "Task A" (ZeroMQ)

    sock_B: Socket = ctx.socket(zmq.PULL)
    sock_B.bind('tcp://*:25001')
    task_B = create_task(update_from_client(gs, sock_B))

    sock_C: Socket = ctx.socket(zmq.PUB)
    sock_C.bind('tcp://*:25000')
    task_C = create_task(push_game_state(gs, sock_C))

    try:
        await asyncio.wait([task_B, task_C, fut], return_when=asyncio.FIRST_COMPLETED)
    except CancelledError:
        print('Cancelled')
    finally:
        sock_B.close(1)
        sock_C.close(1)
        ctx.destroy(linger=1)


if __name__ == '__main__':
    run(main())
