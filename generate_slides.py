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

    slides = [
        slide_title(),
        # slide_warning_flickering(),
        slide_about_me(),

        slide_python_arcade(),
        slide_arcade_docs(),
        slide_why_arcade(),
        slide_lots_of_examples(),
        slide_run_examples(),

        slide_big_picture(),
        slide_tip_vector(),

        slide_get_started_intro(),
        slide_getting_started(),
        slide_keyspressed(),

        slide_tip_save(),
        slide_lag_compensation(),

        slide_shall(),
        slide_fortnite(),
        slide_sc2(),
        slide_awesomenauts(),

        slide_network_models(),
        slide_strategy(),

        slide_basic_networking(),
        slide_tcp_udp(),
        slide_zmq_excuse(),
        slide_zmq(),
        slide_zmq_demo(),

        slide_transmit_inputs(),
        slide_transmit_gamestate(),

        slide_client_interpolation(),
        slide_client_interpolation_2(),
    ]

    output = tmpl.safe_substitute(
        slides='\n'.join(str(s) for s in slides)
    )
    print(output)
    with open('reveal/reveal.js-3.6.0/indexgen.html', 'w', encoding='utf-8') as f:
        f.write(output)


    print('Total slides: ', len(slides))


@section
def slide_title():
    h1('multiplayer 2D gaming')
    h2('with python-arcade')
    with p(style='font-size: 0.8em'):
        text('@caleb_hattingh ● ')
        a('github.com/cjrh', href='github.com/cjrh')
    button('server02', cls='runprogram', cmd='demos.server02')
    button('client02', cls='runprogram', cmd='demos.client02')


@section
def slide_warning_flickering():
    h2('WARNING')
    h3('Screen flickering later')


@section
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


@section
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

@section
def slide_arcade_docs():
    img(src='/img/arcade_doc_screenshot.png')


@section
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


@section
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



@section
def slide_run_examples():
    h2('lots of examples')
    exnames = ['bouncing_ball', 'drawing_text', 'full_screen_example',
               'sprite_move_keyboard']
    with ul():
        for example in exnames:
            cmd = f'arcade.examples.{example}'
            with code_bullet(btn_text=example, cmd=cmd):
                text('(venv) $ python -m arcade.examples.')
                mark(example)



@section
def slide_big_picture():
    h2('The Big Picture')
    p('picture of server and networked pcs')


@section
def slide_get_started_intro():
    h2('Rapid Intro to Python-Arcade')


@section(style='top: 50px')
def slide_getting_started():
    h2('Getting started')
    code_path = pathlib.Path('demos') / 'getting_started.py'
    with pre(style='font-size: 0.4em'):
        with code(cls='hljs python', data_trim='true',
                  style='max-height: unset'):
            with open(code_path) as f:
                text(f.read())
    button('getting_started.py', cls='runprogram', cmd='demos.getting_started')


@section
def slide_keyspressed():
    h2('"Movement" utils')
    import inspect
    code_text = inspect.getsource(demos.movement)
    with pre(style='font-size: 0.4em'):
        with code(cls='hljs python', data_trim='true',
                  style='max-height: unset'):
            text(code_text)
    button('Normalize your movement vector!',
           cls='runprogram', cmd='demos.getting_started_norm')

# Here we should sketch out a basic attack strategy


@section
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
                    strong('Loop A: ')
                    text('send player input (keyboard, mouse) '
                         'e.g. 30 Hz')
                with lip():
                    strong('Loop B: ')
                    text('receive game state (position, health) '
                         'from server')
                with lip():
                    strong('Loop C: ')
                    text('draw game state on screen')
        with div(cls='col', style='padding: 10px'):
            h3('Server')
            with ol():
                with lip():
                    strong('Loop A: ')
                    text('accept client connections')
                with lip():
                    strong('Loop B: ')
                    with ol():
                        li('receive player input')
                        li('update game state')
                with lip():
                    strong('Loop C: ')
                    text('send game state to clients, e.g. 60 Hz')

    p('Each of the internal loops runs independently.',
      cls='fragment')


@section
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

@section
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

@section
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


def slide_shall():
    return section(data_background_image='/img/shallplaygame.jpg')

def slide_fortnite():
    return section(data_background_image='/img/fortnite3.jpg')


def slide_sc2():
    return section(data_background_image='/img/starcraft2.jpg')


def slide_awesomenauts():
    return section(data_background_image='/img/awesomenautsplay.jpg')


@section
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


@section
def slide_basic_networking():
    h2('Basic networking')
    p('(assume client-server)', style='font-size: 0.7em;')
    with ul():
        li('TCP versus UDP')
        li('Player inputs: client 🠊server')
        li('Game state: client 🠈 server')


@section
def slide_tcp_udp():
    h2('TCP vs UDP')
    with ul():
        with li(cls='fragment'):
            text('TCP is ')
            strong('too ')
            text('reliable')
            with ul():
                    li('Dropped packets causes latency (bad!)')
                    li("Sometimes packet loss is ok")
        with li(cls='fragment'):
            text('UDP chosen for ')
            u('control')
            text(' (not speed)')
            with ul():
                li('Can choose when to allow packet loss...')
                li("BUT: it's much more work")
    # TODO: maybe an image showing how one lost packet causes a bunch of
    # others to wait.


@section
def slide_zmq_excuse():
    with p():
        text("But I don't have time to show UDP in this talk!.")
    img(src='/img/greenninja.jpg')
    with p():
        text("Instead, we'll just show TCP (and ZeroMQ) for simplicity.")


@section
def slide_zmq():
    h2('Brief intro to ZeroMQ')
    p('ZeroMQ has "magic" sockets')
    with ul():
        with li(cls='fragment'):
            text('Handling player inputs')
            with ul():
                li('PUSH and PULL sockets')
                li('all clients push to a single server')

        with li(cls='fragment'):
            text('Handling game state')
            with ul():
                li('PUB and SUB sockets')
                li('Server pushes to all clients')


@section
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
                            sock = ctx.socket()
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
                            sock = ctx.socket()
                            sock.bind('127.0.0.1', 9999)
                            while True:
                                payload = await sock.recv_json()
                                await q.put()
                            
                            ctx.destroy()
                    '''))



@section
def slide_transmit_inputs():
    h2('Client: send player input to server')


@section
def slide_transmit_gamestate():
    h2('Server: send game state to client')


@section
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

@section
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

if __name__ == '__main__':
    main()
