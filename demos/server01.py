import logging
import sys
import asyncio
from contextlib import suppress
from typing import Dict, Tuple


logger = logging.getLogger(__name__)


class Player:
    def __init__(self, transport, addr):
        self.transport = transport
        self.addr = addr

    def send(self, new_state):
        self.transport.sendto(new_state, self.addr)


def handle_cancellation(f):
    async def inner(*args, **kwargs):
        with suppress(asyncio.CancelledError):
            return await f(*args, **kwargs)
    return inner


class ServerProtocol:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.state_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.input_queue: asyncio.Queue[Tuple[Player, bytes]] = asyncio.Queue()
        self.brain_task = loop.create_task(self.game_brain())
        self.state_sender_task = loop.create_task(self.state_sender())

    def connection_made(self, transport):
        logger.info('connection made')
        self.transport = transport

    def connection_lost(self, transport):
        logger.info('Connection lost')

    @handle_cancellation
    async def game_brain(self):
        while True:
            player, new_input = await self.input_queue.get()
            new_state = b'new state!'  # This is a big calculation
            await self.state_queue.put(new_state)

    @handle_cancellation
    async def state_sender(self):
        # print('start up state sender')
        while True:
            new_state = await self.state_queue.get()
            # All players get the new game state
            for p in self.players.values():
                p.send(new_state)

    def datagram_received(self, data, addr):
        if data == b'JOIN':
            self.players[addr] = Player(self.transport, addr)
            return
        elif data == b'LEAVE':
            del self.players[addr]
            return

        # This means game input was received.
        message = data.decode()
        logger.debug('Received %r from %s' % (message, addr))
        logger.debug('Send %r to %s' % (message, addr))
        new_input = (self.players[addr], data)
        self.input_queue.put_nowait(new_input)


async def main():
    listen = loop.create_datagram_endpoint(
        ServerProtocol, local_addr=('127.0.0.1', 25000)
    )
    transport, protocol = await listen
    try:
        await asyncio.sleep(100000)
    except asyncio.CancelledError:
        transport.close()


if __name__ == '__main__':
    if 0 and sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
    loop.close()
