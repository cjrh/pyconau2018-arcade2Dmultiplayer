import sys
from aiohttp import web
import subprocess as sp

routes = web.RouteTableDef()

FILENAME = 'reveal/reveal.js-3.6.0/index.html'
if len(sys.argv) > 1:
    FILENAME = f'reveal/reveal.js-3.6.0/{sys.argv[1]}'

@routes.get('/')
async def handle(request):
    return web.FileResponse(FILENAME)


@routes.post('/runprog')
async def runprog(request):
    data = await request.json()
    print(data)
    if 'cmd' in data:
        fname = data['cmd']
        sp.Popen(
            f'python -m demos.{fname}'.split(),
        )

    return web.Response()


app = web.Application()
# app.router.add_static('/', 'reveal/reveal.js-3.6.0/')
app.router.add_static('/js', 'reveal/reveal.js-3.6.0/js')
app.router.add_static('/css', 'reveal/reveal.js-3.6.0/css')
app.router.add_static('/img', 'reveal/reveal.js-3.6.0/img')
app.router.add_static('/lib', 'reveal/reveal.js-3.6.0/lib')
app.router.add_static('/plugin', 'reveal/reveal.js-3.6.0/plugin')

app.router.add_routes(routes)

# app.add_routes([
#     web.get('/', handle),
# ])

print('Serving on http://localhost:8080')
web.run_app(app)
