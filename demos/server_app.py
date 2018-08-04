import sys
import asyncio
import tkinter as tk
import tkinter.ttk as ttk
import datetime


class App(tk.Tk):

    def __init__(self, signal: asyncio.Future=None, interval=0.01):
        super().__init__()
        self.title('Game Server')
        self.loop = asyncio.get_event_loop()
        self.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.loop.create_task(self.close())
        )
        self.tasks = []
        self.create_widgets()
        self.tasks.append(self.loop.create_task(self.updater(interval)))
        self.signal = signal

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.hello = tk.Label(self, text='Server Output', bg='white')
        self.dtime = tk.Label(self)
        self.hello.grid(column=0, row=0)
        self.dtime.grid(column=0, row=1)
        self.output = tk.Text(self)
        self.output.configure(font=("Consolas", 12, "bold"))
        self.output.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.tasks.append(self.loop.create_task(self.clock(1)))
        self.tasks.append(self.loop.create_task(
            self.bg_flip(.337, self.hello, 'red')))

        # Override stdout to write into the text box!
        output = self.output
        class New_stdout:
            def __init__(self):
                self.count = 0

            def write(self, data, *args, **kwargs):
                self.count += 1
                if self.count == 100:
                    output.delete(1.0, 2.0)
                    self.count -= 2
                output.insert('end', data)
                output.see(tk.END)

        self.original_stdout = sys.stdout
        sys.stdout = New_stdout()

    async def clock(self, interval):
        while True:
            self.dtime['text'] = datetime.datetime.now()
            await asyncio.sleep(interval)

    async def bg_flip(self, interval, widget, color):
        while True:
            await asyncio.sleep(interval)
            bg = widget['bg']
            widget['bg'] = color if bg == 'white' else 'white'

    async def updater(self, interval):
        while True:
            self.update()
            # self.update_idletasks()
            await asyncio.sleep(interval)
            # self.loop.call_later(interval, self.updater, interval)

    async def close(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        sys.stdout = self.original_stdout
        if self.signal:
            self.signal.set_result(True)
        self.destroy()


if __name__ == '__main__':
    app = App()
    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()

