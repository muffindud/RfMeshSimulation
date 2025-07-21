from os import getenv
from uuid import uuid4

from httpx import AsyncClient
from quart import Quart, request

from src.Message import Message
from src.Header import Header


ROLE = getenv("MODULE_ROLE", "worker")
NETWORK_HOST = getenv("NETWORK_HOST", "localhost")
NETWORK_PORT = getenv("NETWORK_PORT", 8000)
NETWORK_URI = f"http://{NETWORK_HOST}:{NETWORK_PORT}"

SELF_ID = uuid4()

app = Quart(__name__)


async def register_module():
    async with AsyncClient as client:
        await client.post(f"{NETWORK_URI}/subscribe/{ROLE}/{SELF_ID}")


@app.route('/receive', methods=['POST'])
async def receive():
    message: Message = Message.create_message(await request.get_data())

    if message.header == Header.ACK:
        ...

    elif message.header == Header.DATA:
        ...

    elif message.header == Header.SYNC:
        ...


if __name__ == '__main__':
    register_module()

    app.run(
        host="0.0.0.0",
        port=getenv("MODULE_PORT", 5000)
    )
