import threading
import asyncio

async def io_work():
    while True:
        print('Hi from another thread!')
        await asyncio.sleep(1)

def thread_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)   # <<----- IMPORTANT!!
    loop.create_task(io_work())
    loop.run_forever()

thread = threading.Thread(target=thread_worker())
thread.start()
thread.join()
