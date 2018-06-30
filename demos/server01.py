import logging
import sys
import asyncio


CLIENTS = set()

class Player:
    def __init__(self):
        self.queue_input = asyncio.Queue()
        self.queue_state = asyncio.Queue()


class ServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
        self.player = Player()
        self.sender_task = loop.create_task(self.sender())
        CLIENTS.add(self.player)

    def connection_lost(self, transport):
        # transport will be None
        print('Connection lost')
        CLIENTS.remove(self.player)
        self.sender_task.cancel()

    async def sender(self):
        try:
            while True:
                state = await self.player.queue_state.get()
                self.transport.sendto(state, self.addr)
        except asyncio.CancelledError:
            pass

    def datagram_received(self, data, addr):
        self.addr = addr
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.player.queue_input.put_nowait(data)
        # Wait here until response is ready to go?
        # self.transport.sendto(data, addr)


async def main():
    loop = asyncio.get_event_loop()
    listen = loop.create_datagram_endpoint(
        ServerProtocol, local_addr=('127.0.0.1', 25000)
    )
    transport, protocol = loop.run_until_complete(listen)
    try:
        await asyncio.sleep(100000)
    except asyncio.CancelledError:
        transport.close()


if __name__ == '__main__':
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
    loop.close()
