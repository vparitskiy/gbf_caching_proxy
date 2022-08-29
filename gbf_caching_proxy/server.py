import os
import logging
from pathlib import Path

import aiofiles
import httpx
import xxhash
import uvicorn

from starlette.applications import Starlette
from starlette.responses import Response, FileResponse
from starlette.routing import Route

logger = logging.getLogger("uvicorn.error")


def get_cache_path(url: str) -> Path:
    cache_filename = xxhash.xxh64(url).hexdigest()
    return Path(__file__).parent.parent / 'cache' / cache_filename


async def write_file(response) -> None:
    url = str(response.url)
    headers = response.headers
    content_type = headers['Content-Type'].lower()

    if response.status_code == 200 and content_type in {'image/png', 'image/jpeg', 'audio/mpeg',
                                                        'application/font-woff'}:
        cache_path = get_cache_path(url)
        content = await response.aread()
        logger.warning(f'Cache miss: {url} ({cache_path})')
        async with aiofiles.open(cache_path, 'wb') as f:
            await f.write(content)
        if os.stat(cache_path).st_size == 0:
            os.remove(cache_path)


client = httpx.AsyncClient(event_hooks={'response': [write_file]})


async def serve_proxy_pac_config(request):
    content = b'''function FindProxyForURL(a,b){return shExpMatch(a,"*granbluefantasy.akamaized.net/*")?"PROXY 127.0.0.1:8899; DIRECT":"DIRECT"}'''
    return Response(content, media_type='application/x-ns-proxy-autoconfig')


async def handle_get(request):
    url = str(request.url)
    cache_path = get_cache_path(url)

    if cache_path.exists():
        logger.info(f'Cache hit: {url} ({cache_path})')
        headers = {'Content-Encoding': 'identity', 'Access-Control-Allow-Origin': '*',
                   'Content-Type': 'application/octet-stream'}
        return FileResponse(cache_path, headers=headers)

    response = await client.get(url, headers=dict(request.headers))
    return await handle_response(response)


async def handle_post(request):
    url = str(request.url)
    response = await client.post(url, headers=dict(request.headers), content=await request.body())
    return await handle_response(response)


async def handle_response(response):
    content = await response.aread()
    headers = response.headers
    if headers.get('Content-Encoding', '').lower() == 'gzip':
        headers['Content-Encoding'] = 'identity'
        headers['Content-Length'] = str(len(content))

    return Response(
        content, headers=headers, media_type=response.headers['Content-Type'], status_code=response.status_code
    )


routes = [
    Route('/proxy-pac-config', endpoint=serve_proxy_pac_config),
    Route('/{path:path}', endpoint=handle_get, methods=['GET']),
    Route('/{path:path}', endpoint=handle_post, methods=['POST']),
]

app = Starlette(debug=False, routes=routes)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8899)
