from aiohttp import web
import os
import asyncio

file_storage = {}
playback_positions = {}

async def upload_music(request):
    data = await request.json()
    try:
        chat_id = int(data['chat_id'])
    except (ValueError, TypeError):
        return web.json_response({"status": "error", "message": "chat_id must be an integer"}, status=400)
    
    file_path = data['file_path']
    if not os.path.exists(file_path):
        return web.json_response({"status": "error", "message": "File not found"}, status=404)

    file_storage[chat_id] = file_path
    playback_positions[chat_id] = 0
    return web.json_response({"status": "uploaded", "chat_id": chat_id})

async def stream_music(request):
    chat_id_param = request.query.get('chat_id')
    try:
        chat_id = int(chat_id_param)
    except (ValueError, TypeError):
        return web.Response(status=400, text="chat_id must be an integer as a query parameter")

    file_path = file_storage.get(chat_id)
    if not file_path or not os.path.exists(file_path):
        return web.Response(status=404, text="Music not found")
    
    range_header = request.headers.get("Range", None)
    start = playback_positions.get(chat_id, 0)
    if range_header:
        start = int(range_header.split('=')[1].split('-')[0])
    
    async def stream(file_path, start):
        with open(file_path, 'rb') as f:
            f.seek(start)
            while chunk := f.read(8192):
                yield chunk
                playback_positions[chat_id] += len(chunk)
                await asyncio.sleep(0.1)

    return web.Response(body=stream(file_path, start), status=206, headers={
        'Content-Type': 'audio/mpeg',
        'Content-Range': f"bytes {start}-",
    })

async def player_page(request):
    return web.FileResponse("src/player.html")

app = web.Application()
app.add_routes([web.post('/upload', upload_music),
                web.get('/play', stream_music),
                web.get('/', player_page)])

if __name__ == '__main__':
    web.run_app(app, port=8080)
