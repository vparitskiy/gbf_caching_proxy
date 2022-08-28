import os
from pathlib import Path
from typing import Optional
import httpx
import aiofiles
import xxhash
import uvicorn
from sanic import Sanic
from sanic.response import raw
from starlette.applications import Starlette
from starlette.responses import Response, FileResponse
from starlette.routing import Route


async def write_file(path, content):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(content)
    if os.stat(path).st_size == 0:
        os.remove(path)


async def serve_proxy_pac(request):
    return FileResponse('gbf-proxy.pac', media_type='application/x-ns-proxy-autoconfig')


async def handle_get(request):
    url = str(request.url)
    cache_filename = xxhash.xxh64(url).hexdigest()
    cache_path = Path(__file__).parent / 'cache' / cache_filename

    if cache_path.exists():
        headers = {'Content-Encoding': 'identity', 'Access-Control-Allow-Origin': '*'}
        return FileResponse(cache_path, headers=headers)

    response = httpx.get(url, headers=dict(request.headers))
    headers = response.headers
    content_type = headers['Content-Type'].lower()

    if cache_filename and content_type in {'image/png', 'image/jpeg', 'audio/mpeg', 'application/font-woff'}:
        await write_file(cache_path, response.content)

    return await handle_response(response)


async def handle_post(request):
    url = str(request.url)
    response = httpx.post(url, headers=dict(request.headers), content=await request.body())
    return await handle_response(response)


async def handle_response(response):
    content = response.content
    headers = response.headers
    if headers.get('Content-Encoding', '').lower() == 'gzip':
        headers['Content-Encoding'] = 'identity'
        headers['Content-Length'] = str(len(content))

    return Response(
        content, headers=headers, media_type=response.headers['Content-Type'], status_code=response.status_code
    )


routes = [
    Route('/gbf-proxy.pac', endpoint=serve_proxy_pac),
    Route('/{path:path}', endpoint=handle_get, methods=['GET']),
    Route('/{path:path}', endpoint=handle_post, methods=['POST']),
]

app = Starlette(debug=False, routes=routes)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8899)
