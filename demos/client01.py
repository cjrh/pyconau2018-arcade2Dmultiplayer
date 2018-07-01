import logging
import asyncio


logger = logging.getLogger(__name__)


class EchoClientProtocol:
    def __init__(self):
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        print('connected')
        self.transport = transport
        print('starting script task')
        loop.create_task(self.script())

    async def script(self):
        self.transport.sendto(b'JOIN')
        for i in range(10):
            await asyncio.sleep(1)
            self.transport.sendto(b'BLAH')

        await asyncio.sleep(1)
        self.transport.sendto(b'LEAVE')
        self.transport.close()

    def datagram_received(self, data, addr):
        print("Received:", data.decode())

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()


async def main():
    connect = loop.create_datagram_endpoint(
        EchoClientProtocol, remote_addr=('127.0.0.1', 25000)
    )
    transport, protocol = await connect
    try:
        await asyncio.sleep(100000)
    except asyncio.CancelledError:
        transport.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
    loop.close()
