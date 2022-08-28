import os
from pathlib import Path
from typing import Optional
import httpx
import aiofiles
import xxhash
from sanic import Sanic
from sanic.response import raw, file


app = Sanic("gbf-caching-proxy")


async def write_file(path, content):
    async with aiofiles.open(path, 'wb') as f:
        await f.write(content)
    if os.stat(path).st_size == 0:
        print(f'Bad file size: {path}')
        os.remove(path)


@app.route('/gbf-proxy.pac')
async def serve_proxy_pac(request):
    print('Serving proxy configuration..')
    return await file('gbf-proxy.pac', mime_type=' application/x-ns-proxy-autoconfig')


@app.route('/<path:path>')
async def handle_get(request, path: Optional[str] = ''):
    cache_filename = xxhash.xxh64((request.url).encode('utf-8')).hexdigest()
    cache_path = Path(__file__).parent / 'cache' / cache_filename

    if cache_path.exists():
        print(f'Cache hit: {request.url} ({cache_path})')
        headers = {'Content-Encoding': 'identity', 'Access-Control-Allow-Origin': '*'}
        return await file(cache_path, headers=headers)

    response = httpx.get(request.url, headers=dict(request.headers))
    headers = response.headers
    content_type = headers['Content-Type'].lower()

    if cache_filename and content_type in {'image/png', 'image/jpeg', 'audio/mpeg', 'application/font-woff'}:
        print(f'Cache miss: {response.url} ({cache_path})')
        await write_file(cache_path, response.content)

    return await handle_response(response)


@app.route('/<path:path>', methods=["POST"])
async def handle_post(request, path: Optional[str] = ''):
    response = httpx.post(request.url, headers=dict(request.headers), data=request.body)
    return await handle_response(response)


async def handle_response(response):
    content = response.content
    headers = response.headers
    if headers.get('Content-Encoding', '').lower() == 'gzip':
        headers['Content-Encoding'] = 'identity'
        headers['Content-Length'] = str(len(content))
    return raw(content, headers=headers, content_type=response.headers['Content-Type'], status=response.status_code)


if __name__ == '__main__':
    app.run()
