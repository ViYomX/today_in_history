from aiohttp import web
import os
import asyncio

file_storage = {}
playback_state = {}

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
    playback_state[chat_id] = 'playing'
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
    
    async def stream(file_path):
        while True:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
                    await asyncio.sleep(0.1)
    
    return web.Response(body=stream(file_path), headers={'Content-Type': 'audio/mpeg'})

async def player_page(request):
    return web.FileResponse("src/player.html")

async def play_page(request):
    return web.FileResponse("src/play.html")

async def get_state(request):
    chat_id_param = request.query.get('chat_id')
    try:
        chat_id = int(chat_id_param)
    except (ValueError, TypeError):
        return web.json_response({"status": "error", "message": "chat_id must be an integer"}, status=400)

    state = playback_state.get(chat_id, 'playing')
    return web.json_response({"status": state})

async def update_state(request):
    data = await request.json()
    try:
        chat_id = int(data['chat_id'])
        state = data['state']
        if state not in ['playing', 'paused']:
            raise ValueError("Invalid state")
    except (ValueError, TypeError, KeyError):
        return web.json_response({"status": "error", "message": "Invalid chat_id or state"}, status=400)

    playback_state[chat_id] = state
    return web.json_response({"status": "success", "chat_id": chat_id, "state": state})

app = web.Application()
app.add_routes([web.post('/upload', upload_music),
                web.get('/stream', stream_music),
                web.get('/play', play_page),
                web.get('/', player_page),
                web.get('/state', get_state),
                web.post('/state', update_state)])

if __name__ == '__main__':
    web.run_app(app, port=8080)
