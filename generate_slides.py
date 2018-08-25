from collections import deque
from contextlib import contextmanager
from string import Template
from textwrap import dedent

import dominate
from dominate.tags import *
from dominate.util import text
import arcade.examples
import pathlib
import math
import demos.lib02
import demos.movement


def main():
    with open('reveal/reveal.js-3.6.0/index.html.template',
              encoding='utf-8') as f:
        tmpl = Template(f.read())

    # slides = [
    #     slide_title(),
    #     # slide_warning_flickering(),
    #     slide_about_me(),
    #
    #     slide_python_arcade(),
    #     slide_arcade_docs(),
    #     slide_why_arcade(),
    #     slide_lots_of_examples(),
    #     slide_run_examples(),
    #
    #     slide_big_picture(),
    #     slide_tip_vector(),
    #
    #     slide_get_started_intro(),
    #     slide_getting_started(),
    #     slide_keyspressed(),
    #
    #     slide_tip_save(),
    #     slide_lag_compensation(),
    #
    #     slide_shall(),
    #     slide_fortnite(),
    #     slide_sc2(),
    #     slide_awesomenauts(),
    #
    #     slide_network_models(),
    #     slide_strategy(),
    #
    #     slide_basic_networking(),
    #     slide_tcp_udp(),
    #     slide_zmq_excuse(),
    #     slide_zmq(),
    #     slide_zmq_demo(),
    #
    #     slide_transmit_inputs(),
    #     slide_transmit_gamestate(),
    #
    #     slide_client_interpolation(),
    #     slide_client_interpolation_2(),
    # ]

    output = tmpl.safe_substitute(
        slides='\n'.join(str(s) for s in slides)
    )
    print(output)
    with open('reveal/reveal.js-3.6.0/indexgen.html', 'w', encoding='utf-8') as f:
        f.write(output)

    print('Total slides: ', len(slides))


slides = []


def add_slide(f):
    @section
    def inner(*args, **kwargs):
        f(*args, **kwargs)

    slides.append(inner())


def add_slide_plain(f):
    @section
    def inner(*args, **kwargs):
        f(*args, **kwargs)

    slides.append(inner())


def add_slide50(f):
    @section(style='top: 50px')
    def inner(*args, **kwargs):
        f(*args, **kwargs)

    slides.append(inner())


def code_block(filename, lines=None, size='0.4em', highlights=None):
    code_path = pathlib.Path('demos') / filename
    with pre(style=f'font-size: {size}'):
        with code(cls='hljs python', data_trim='true',
                  style='max-height: unset',
                  data_noescape='true'
                  ):
            with open(code_path) as f:
                data = f.readlines()
            if lines:
                data = data[slice(lines[0] - 1, lines[1] - 0)]
            content = ''.join(data)
            if highlights:
                c = content
                for s in highlights:
                    a, b, c = c.partition(s)
                    text(a)
                    mark(b)
                text(c)
            else:
                text(''.join(data))


@add_slide
def slide_title():
    h1('multiplayer 2D gaming')
    h2('with python-arcade')
    with p(style='font-size: 0.7em'):
        text('@caleb_hattingh ● ')
        # a('github.com/cjrh', href='github.com/cjrh')
        a('github.com/cjrh/pyconau2018-arcade2Dmultiplayer', href='github.com/cjrh/pyconau2018-arcade2Dmultiplayer')

    button('server02', cls='runprogram', cmd='demos.server02')
    button('client02', cls='runprogram', cmd='demos.client02')


@add_slide
def slide_goals():
    h2('Goals')
    with p():
        text('Build a simple multiplayer game!')


@add_slide
def slide_goals():
    h2('Goals')
    with p():
        s('Build a simple multiplayer game!')
    div(style='margin-top: 30px;')
    p('Show & tell the building blocks')


@add_slide
def slide_about_me():
    h2('about me')
    with ul():
        with li():
            with p():
                text('Network automation at ')
                img(src='/img/pccwglobal.png', height=42, style='vertical-align:middle;')
        # li('"Network Automation" at PCCW Global')
        li("Books and videos at O'Reilly Safari:")
    with div():
        img(src='/img/cythoncover.jpg', height=250)
        img(src='/img/20libscover.png', height=250)
        with div(style='display: inline-block'):
            p('April 2018!', style='font-size: 0.6em; margin: 0')
            img(src='/img/aiocover.png', height=250)
    a('https://www.safaribooksonline.com/search/?query=caleb%20hattingh',
      href='https://www.safaribooksonline.com/search/?query=caleb%20hattingh',
      style='font-size: 0.6em;')


@add_slide
def slide_python_arcade():
    h2('Python-Arcade')
    with p():
        text('created by Paul Craven ●')
        a('http://arcade.academy', href='http://arcade.academy')
    with div(style='display: flex; margin: auto'):
        img(data_src='img/penguin.png', width=48, height=48)
        with pre():
            with code(cls='hljs bash', data_trim=True,
                      contenteditable=True):
                text('''\
                    (venv) $ pip install arcade
                ''')
    with div(style='display: flex; margin: auto'):
        img(data_src='img/windows_icon.png', width=48, height=48)
        with pre():
            with code(cls='hljs cmd', data_trim=True,
                      contenteditable=True):
                text('''\
                    (venv) C:\mygame> pip install arcade
                ''')


@add_slide
def slide_arcade_docs():
    img(src='/img/arcade_doc_screenshot.png')


@add_slide
def slide_why_arcade():
    h2('Why Python-Arcade?')
    with ul():
        li('Easy to install')
        li('OpenGL (via Pyglet)')
        li('Modern (Python 3 only, type annotations)')
        with li():
            code('(0, 0)')
            text(' is at the bottom-left')
        li('Very clean, simple API')
        with li(cls='fragment'):
            strong('Examples 🎁🎁🎁')


@add_slide
def slide_lots_of_examples():
    with h2():
        u('lots')
        text(' of examples')

    examples_path = pathlib.Path(arcade.examples.__file__)
    examples_dir = examples_path.parent
    examples = deque(sorted(
        f.name for f in filter(
            lambda x: x.suffix == '.py' and x.name != '__init__.py',
            list(examples_dir.iterdir()))
    ))

    columns = 3
    column_height = math.ceil(len(examples) / columns)

    with div(cls='container', style='font-size: 0.3em;'):
        for i in range(columns):
            with div(cls='col'):
                for j in range(column_height):
                    if examples:
                        p(examples.popleft())


@contextmanager
def code_bullet(btn_text='', cmd=''):
    with li():
        with pre():
            with code(cls='hljs bash', data_trim='true',
                      contenteditable='true', data_noescape='true'):
                yield
        if btn_text:
            button(
                btn_text,
                cls='runprogram',
                cmd=cmd)


@add_slide
def slide_run_examples():
    h2('lots of examples')
    exnames = ['bouncing_ball', 'sprite_collect_coins',
               'sprite_move_keyboard']
    with ul():
        for example in exnames:
            cmd = f'arcade.examples.{example}'
            with code_bullet(btn_text=example, cmd=cmd):
                text('(venv) $ python -m arcade.examples.')
                mark(example)


@add_slide
def slide_get_started_intro():
    h2('Intro: Python-Arcade')


@add_slide50
def slide_getting_started():
    h2('Getting started')
    code_block('getting_started.py',
               highlights=[
                   'def update',
                   'def on_draw',
                   'def on_key_press',
                   'def on_key_release',
               ])
    button('getting_started.py', cls='runprogram', cmd='demos.getting_started')


@add_slide50
def slide_getting_started():
    h2('Getting started')
    code_block('getting_started.py',
               highlights=[
                   'self.keys_pressed',
                   'apply_movement',
                   'self.keys_pressed.keys[key] = True',
                   'self.keys_pressed.keys[key] = False',
               ])
    button('getting_started.py', cls='runprogram', cmd='demos.getting_started')


@add_slide
def slide_keyspressed():
    h2('"Movement" utils')
    import inspect
    code_block('movement.py',
               size='0.5em',
               highlights=[
                   'current_position + delta_position * speed * dt'
               ])


@add_slide
def slide_tip_vector():
    h2('🎁tip #1: use a vector class')
    with p():
        text('Use the one in ')
        strong('pymunk')

    with pre():
        with code(cls='hljs python', data_trim='true', contenteditable='true'):
            text(dedent('''\
                >>> from pymunk.vec2d import Vec2d
                >>> pixel = Vec2d(3, 4)
                >>> pixel.x
                3
                >>> pixel.y
                4
                >>>
                >>> pixel + 2 * pixel
                Vec2d(9, 12)
                >>> pixel.length
                5.0
                >>> pixel.length = 1
                >>> pixel
                Vec2d(0.6, 0.8)
            '''))


@add_slide
def slide_keyspressed():
    h2('"Movement" utils')
    import inspect
    # code_text = inspect.getsource(demos.movement)
    code_block('movement.py',
               size='0.5em',
               highlights=['.normalized()'])
    # with pre(style='font-size: 0.4em'):
    #     with code(cls='hljs python', data_trim='true',
    #               style='max-height: unset'):
    #         text(code_text)
    button('Normalize your movement vector!',
           cls='runprogram', cmd='demos.getting_started_norm')


# @add_slide
def slide_lag_compensation():
    p(dedent('''\
Good discussion about lag compensation

https://www.reddit.com/r/Overwatch/comments/3u5kfg/everything_you_need_to_know_about_tick_rate/
https://en.wikipedia.org/wiki/Netcode
https://www.pcgamer.com/netcode-explained/

Some python code here:

https://www.gamedev.net/forums/topic/652377-network-tick-rates/

Book on safari:
https://www.safaribooksonline.com/library/view/fundamentals-of-network/9781584505570/ch01.html    
    '''))


@add_slide_plain
def slide_shall():
    return section(data_background_image='/img/shallplaygame.jpg')


@add_slide_plain
def slide_fortnite():
    return section(data_background_image='/img/fortnite3.jpg')


@add_slide_plain
def slide_sc2():
    return section(data_background_image='/img/starcraft2.jpg')


@add_slide_plain
def slide_awesomenauts():
    return section(data_background_image='/img/awesomenautsplay.jpg')


@add_slide
def slide_network_models():
    h2('Network models')
    with section():
        with ol():
            with li(cls='fragment'):
                strong('Client-server: ')
                text('clients only "capture inputs"')
                with ul(style='font-size: 0.7em;'):
                    examples = ['Fortnite', 'Quake', 'Unreal Tournament', 'Overwatch']
                    for ex in examples:
                        li(ex)
            with li(cls='fragment'):
                strong('Peer-to-peer (lockstep): ')
                text('synced sim on each client')
                with ul(style='font-size: 0.7em;'):
                    examples = ['Command & Conquer', 'Age of Empires',
                                'StarCraft', 'Supreme Commander 2']
                    for ex in examples:
                        li(ex)
            with li(cls='fragment'):
                strong('Peer-to-peer: ')
                text('each client calculates self')
                with ul(style='font-size: 0.7em;'):
                    examples = ['Awesomenauts']
                    for ex in examples:
                        li(ex)

    with section():
        links = [
            a('What every programmer needs to know about game networking - Glenn Fiedler',
              href='https://gafferongames.com/post/what_every_programmer_needs_to_know_about_game_networking/'),
            a('Core network structures for games - Joost van Dongen',
              href='http://joostdevblog.blogspot.com/2014/09/core-network-structures-for-games.html'),
            a('Source Multiplayer Networking - Valve',
              href='https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking'),
        ]

        p('References', style='font-size: 0.6em')
        for link in links:
            p(link, style='font-size: 0.6em')


@add_slide
def slide_big_picture():
    h2('Client-server: The Big Picture')
    img(src='/img/server-based-network.svg', width=500)


@add_slide
def slide_basic_networking():
    h2('Communication')
    with ol():
        li('Player inputs: client 🠊 server')
        li('Game state: client 🠈 server')
        li('TCP versus UDP')


@add_slide
def player_inputs():
    h2('1. Player input state')
    p('send client 🠊 server')
    with ul():
        with li():
            b('inputs ')
            text('not "speed" or "position"')
        li('Use dataclasses:')

    code_path = pathlib.Path('demos') / 'player_event.py'
    with pre(style='font-size: 0.4em'):
        with code(cls='hljs python', data_trim='true', style='max-height: unset'):
            with open(code_path) as f:
                text(f.read())


@add_slide
def game_state():
    h2('2. Game state')
    p('send server 🠊 client')
    code_block('game_state.py')


@add_slide
def slide_tcp_udp():
    h2('3. TCP vs UDP')
    with ul():
        with li(cls='fragment'):
            text('Problem: TCP is ')
            strong('too ')
            text('reliable')
            with ul():
                li('Dropped packets causes latency (bad!)')
                li("Sometimes packet loss is ok")
        with li(cls='fragment'):
            text('UDP chosen for ')
            u('control')
            text(' (not merely speed)')
            with ul():
                li('Can choose when to allow packet loss...')
                li("BUT: it's much more work")
    # TODO: maybe an image showing how one lost packet causes a bunch of
    # others to wait.


@add_slide
def slide_zmq_excuse():
    with p():
        text("No time for UDP!")
    img(src='/img/greenninja.jpg')
    with p():
        text("Instead, we'll just show TCP (and ZeroMQ) for simplicity.")


@add_slide
def slide_zmq():
    h2('Brief intro to ZeroMQ')
    p('Thin abstraction over TCP ● "magic" sockets')
    with ul():
        with li(cls='fragment'):
            text('Handling player inputs')
            with ul():
                with li():
                    b('PUSH + PULL ')
                    text('sockets')
                li('all clients push to a single server')

        with li(cls='fragment'):
            text('Handling game state')
            with ul():
                with li():
                    b('PUB + SUB ')
                    text('sockets')
                li('Server pushes to all clients')


@add_slide
def slide_zmq_demo():
    h2('ZMQ client & server')
    with div(cls='container'):
        with div(cls='col', style='padding: 10px'):
            h3('Client (player)')
            with pre():
                with code(cls='hljs python', data_trim='true', contenteditable='true'):
                    text(dedent('''\
                        from asyncio import run, Queue
                        import zmq
                        from zmq.asyncio import Context, Socket

                        async def zmq_push(q: Queue):
                            ctx = Context()
                            sock = ctx.socket(zmq.PUSH)
                            sock.connect('127.0.0.1', 9999)
                            while True:
                                payload: Dict = await q.get()
                                if payload is None: 
                                    break
                                await sock.send_json(payload)
                            
                            ctx.destroy()
                    '''))
        with div(cls='col', style='padding: 10px'):
            h3('Server')
            with pre():
                with code(cls='hljs python', data_trim='true', contenteditable='true'):
                    text(dedent('''\
                        from asyncio import run, Queue
                        import zmq
                        from zmq.asyncio import Context, Socket

                        async def zmq_pull(q: Queue):
                            ctx = Context()
                            sock = ctx.socket(zmq.PULL)
                            sock.bind('127.0.0.1', 9999)
                            while True:
                                payload = await sock.recv_json()
                                await q.put()
                            
                            ctx.destroy()
                    '''))


@add_slide
def where_to_begin():
    h2('Client-server: Components')
    p('where to begin?')


@add_slide
def slide_strategy():
    h2('Client-server: Components')

    def lip(text=None):
        if text:
            return li(text, cls='fragment', style='font-size: 0.7em')
        else:
            return li(cls='fragment', style='font-size: 0.7em')

    with div(cls='container'):
        with div(cls='col', style='padding: 10px'):
            h3('Client')
            with ol():
                lip('client connects to server')
                with lip():
                    strong('Task A: ')
                    text('send player input (keyboard, mouse) '
                         'e.g. 30 Hz')
                with lip():
                    strong('Task B: ')
                    text('receive game state (position, health) '
                         'from server')
                with lip():
                    strong('Task C: ')
                    text('draw game state on screen')
        with div(cls='col', style='padding: 10px'):
            h3('Server')
            with ol():
                with lip():
                    strong('Task A: ')
                    text('accept client connections')
                with lip():
                    strong('Task B: ')
                    with ol():
                        li('receive player input')
                        li('update game state')
                with lip():
                    strong('Task C: ')
                    text('send game state to clients, e.g. 15 Hz')

    p('Each of the internal tasks runs independently.',
      cls='fragment')


@add_slide
def begin_with_server():
    h4("Let's begin with the server")
    p("(It's easier)")


@add_slide
def server_code_main():
    h3("Server code - main (1/2)")
    code_block('server03.py', lines=[44, 67], size='0.5em',
               highlights=[
                   'Task A',
                   'task_B',
                   'task_C'
               ])


@add_slide
def server_code_tasks():
    h3("Server code - task detail (2/2)")
    code_block('server03.py', lines=[15, 42])


# Client code
@add_slide
def client_code1():
    h2('Client code needs TWO loops!')
    with ul():
        li('python-arcade: game loop')
        li('asyncio: IO loop')
        with li():
            b('Cannot ')
            text('run both loops in same thread')

    p('Least-effort solution: run asyncio loop in a thread')
    # mention - because of asyncio, only need 1 extra thread, whereas
    # blocking sockets would need more.


@add_slide
def client_code_whole():
    h3('Client code - main (1/3)')
    code_block('client03.py', size='0.5em', lines=[131, 145],
               highlights=['iomain', 'MyGame']
               )


@add_slide
def client_code_io():
    h3('Client code - iomain thread (2/3)')
    # should also use the "empty" version here
    # rename window.t to window.time_since_state_update
    code_block('client03-empty.py', size='0.4em', lines=[61, 92],
               highlights=['iomain', 'window.player_input',
                           'window.game_state.from_json',
                           'window.player.position'])


@add_slide
def client_code_game():
    h3('Client code - game object (3/3)')
    # Need a version without any prediction!
    # And then later also need a version WITH prediction.
    code_block('client03-empty.py', size='0.4em', lines=[27, 60],
               highlights=['MyGame', 'pass'])

@add_slide
def client_code_interp():
    h2('discuss that we need interp to draw smooth')
    p('compare two buttons - one runs full client side render, other via server.')


@add_slide
def client_code_prediction():
    h2('Show diagram of extrapolation')


@add_slide
def slide_client_interpolation():
    h3('Client-side interpolation')
    with p():
        text('Need to understand ')
        u('motion')
        text(', i.e., speed')
    with script(type='math/text; mode=display'):
        text(dedent(r'''
            v_x = \frac{x_1 - x_0}{t_1 - t_0} \qquad v_y = \frac{y_1 - y_0}{t_1 - t_0}
        '''))
    with p(cls='fragment'):
        text('This describes the past—what about the future?')
    with div(cls='fragment'):
        with script(cls='fragment', type='math/tex; mode=display'):
            text(dedent(r'''
                v_x = \frac{\color{red}{x_2} - x_1}
                {\color{red}{t_2} - t_1} \qquad v_y =
                \frac{\color{red}{y_2} - y_1}{\color{red}{t_2} - t_1}
            '''))


@add_slide
def slide_client_interpolation_2():
    h3('Client-side interpolation')
    with script(type='math/text; mode=display'):
        text(dedent(r'''
            v_x = \frac{\color{red}{x_2} - x_1}
            {\color{red}{t_2} - t_1} \qquad v_y =
            \frac{\color{red}{y_2} - y_1}{\color{red}{t_2} - t_1}
        '''))
    with p(cls='fragment'):
        text('Make the predicted values explicit:')
    with div(cls='fragment'):
        with script(cls='fragment', type='math/tex; mode=display'):
            text(dedent(r'''
                \color{red}{x_2} = v_x \times \Delta t + x_1
                \qquad
                \color{red}{y_2} = v_y \times \Delta t + y_1
            '''))


@add_slide
def client_code_demo_4_updates_per_second():
    h2('demo')


@add_slide
def client_code_demo_10_updates_per_second():
    h2('demo')


@add_slide
def conclusions():
    h2('add conclusions')


@add_slide
def fin():
    p('The end!')


@add_slide
def slide_tip_save():
    h2('🎁tip #2: save & load game data')
    with p():
        text('Use the one in ')
        strong('pyglet')

    # <!--TODO: use pathlib-->
    # <!--TODO: also "appdirs" package: https://pypi.org/project/appdirs/-->

    with pre():
        with code(cls='hljs python', data_trim='true', contenteditable='true'):
            text(dedent('''\
                import os, pyglet.resource, pathlib

                def save_scores(new_scores):
                    game_folder = pyglet.resource.get_settings_path("MyGame")
                    path = pathlib.Path(game_folder, "highscores.txt")
                    path.mkdir(parents=True, exist_ok=True)
                    with path.open("w") as f:
                        f.write(new_scores)
            '''))

    with p(style='font-size: large'):
        text('(pyglet gets installed when you install arcade)')


if __name__ == '__main__':
    main()
