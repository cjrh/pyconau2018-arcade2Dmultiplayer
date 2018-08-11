import asyncio
import time
from asyncio import run, create_task, CancelledError

import zmq
from zmq.asyncio import Context, Socket
from pymunk.vec2d import Vec2d
from .lib02 import PlayerEvent, PlayerState, GameState
from .server_app import App
from demos.movement import KeysPressed, apply_movement


SERVER_UPDATE_TICK_HZ = 10


def update_game_state(gs: GameState, event: PlayerEvent):
    player_state = gs.player_states[0]
    dt = time.time() - (player_state.updated)
    current_position = Vec2d(player_state.x, player_state.y)
    current_position = apply_movement(
        player_state.speed, dt, current_position, event
    )
    player_state.x = current_position.x
    player_state.y = current_position.y

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
    try:
        while True:
            msg = await sock.recv_json()
            counter = msg['counter']
            event_dict = msg['event']
            # event_dict = await sock.recv_json()
            print(f'Got event dict: {event_dict}')
            event = PlayerEvent(**event_dict)
            update_game_state(gs, event)
    except asyncio.CancelledError:
        pass


async def ticker(sock1, sock2):
    ps = PlayerState(speed=500)
    gs = GameState(player_states=[ps], game_seconds=1)
    s = gs.to_json()

    # A task to receive keyboard and mouse inputs from players.
    # This will also update the game state, gs.
    t = create_task(update_from_client(gs, sock2))

    # Send out the game state to all players 60 times per second.
    try:
        while True:
            await sock1.send_string(gs.to_json())
            # print('.', end='', flush=True)
            await asyncio.sleep(1 / SERVER_UPDATE_TICK_HZ)
    except asyncio.CancelledError:
        t.cancel()
        await t


async def main():
    fut = asyncio.Future()
    app = App(signal=fut)
    ctx = Context()

    sock_push_gamestate: Socket = ctx.socket(zmq.PUB)
    sock_push_gamestate.bind('tcp://*:25000')

    sock_recv_player_evts: Socket = ctx.socket(zmq.PULL)
    sock_recv_player_evts.bind('tcp://*:25001')

    ticker_task = asyncio.create_task(
        ticker(sock_push_gamestate, sock_recv_player_evts),
    )
    try:
        await asyncio.wait(
            [ticker_task, fut],
            return_when=asyncio.FIRST_COMPLETED
        )
    except CancelledError:
        print('Cancelled')
    finally:
        ticker_task.cancel()
        await ticker_task
        sock_push_gamestate.close(1)
        sock_recv_player_evts.close(1)
        ctx.destroy(linger=1000)


if __name__ == '__main__':
    run(main())
