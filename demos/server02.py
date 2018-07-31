import asyncio
import time
from asyncio import run, create_task, CancelledError

import zmq
from zmq.asyncio import Context, Socket
from pymunk.vec2d import Vec2d
from .lib02 import PlayerEvent, PlayerState, GameState


SERVER_UPDATE_TICK_HZ = 10


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
        event_dict = await sock.recv_json()
        print(f'Got event dict: {event_dict}')
        event = PlayerEvent(**event_dict)
        update_game_state(gs, event)


async def ticker(sock1, sock2):
    ps = PlayerState(speed=500)
    gs = GameState(player_states=[ps], game_seconds=1)
    s = gs.to_json()

    # A task to receive keyboard and mouse inputs from players.
    # This will also update the game state, gs.
    create_task(update_from_client(gs, sock2))

    # Send out the game state to all players 60 times per second.
    while True:
        await sock1.send_string(gs.to_json())
        # print('.', end='', flush=True)
        await asyncio.sleep(1 / SERVER_UPDATE_TICK_HZ)


async def main():
    ctx = Context()

    sock_push_gamestate: Socket = ctx.socket(zmq.PUB)
    sock_push_gamestate.bind('tcp://*:25000')

    sock_recv_player_evts: Socket = ctx.socket(zmq.PULL)
    sock_recv_player_evts.bind('tcp://*:25001')

    try:
        await ticker(sock_push_gamestate, sock_recv_player_evts)
    except CancelledError:
        print('Cancelled')
    finally:
        sock_push_gamestate.close(1)
        sock_recv_player_evts.close(1)
        ctx.destroy(linger=1)


if __name__ == '__main__':
    run(main())
