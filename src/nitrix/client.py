import asyncio

from nio import AsyncClient
from aiohttp import InvalidURL

# def sync_forever(client):
#     asyncio.run(client.sync_forever(timeout=30000))

async def client_factory(homeserver: str, username: str, password: str) -> AsyncClient | None:
    client = AsyncClient(
            homeserver=homeserver,
            user=username,
            device_id="Nitrix",
        )
    
    try:
        await client.login(password, 'Nitrix')
    except InvalidURL:
        ...
    except Exception as e:
        await client.close()
        raise
    
    if client.logged_in:
        await client.sync()
        loop = asyncio.get_event_loop()
        loop.create_task(client.sync_forever(timeout=30000))
        return client
    
    client.close()