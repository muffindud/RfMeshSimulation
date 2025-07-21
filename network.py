from os import getenv

import random

from quart import Quart, request, jsonify
from httpx import AsyncClient


MODULE_PORT = getenv("MODULE_PORT", 5000)
BRANCHING_FACTOR = (1, 4)

app = Quart(__name__)

# Each key is a node ID, and the value is a list of neighbor node IDs.
network: dict[str, set[str]] = {}

# Each key is a module ID, and the value is the IP address of the module.
module_id_map: dict[str, str] = {}

# Global variable to store the manager ID
manager_id: str | None = None


# Create a two-way link between nodes
def link(module_id: str, neighbor_id: str) -> None:
    if neighbor_id != module_id:
        network[module_id].add(module_id)
        network[neighbor_id].add(module_id)


def create_random_links(module_id: str) -> None:
    if BRANCHING_FACTOR[0] < len(network):
        for node in network.keys():
            link(module_id, node)

    elif BRANCHING_FACTOR[1] < len(network):
        branch_count = random.randint(BRANCHING_FACTOR[0], len(network))
        nodes = random.sample(list(network.keys()), branch_count)

        for node in nodes:
            link(module_id, node)

    else:
        branch_count = random.randint(*BRANCHING_FACTOR)
        nodes = random.sample(list(network.keys()), branch_count)

        for node in nodes:
            link(module_id, node)


@app.route("/subscribe/worker/<string:module_id>", methods=["POST"])
async def subscribe_worker(module_id: str):
    network[module_id] = set()
    module_id_map[module_id] = request.remote_addr
    create_random_links(module_id)
    return jsonify({"status": "subscribed", "module_id": module_id}), 200


@app.route("/subscribe/manager/<string:module_id>", methods=["POST"])
async def subscribe_manager(module_id: str):
    network[module_id] = set()
    module_id_map[module_id] = request.remote_addr
    global manager_id
    manager_id = module_id
    return jsonify({"status": "subscribed", "module_id": module_id}), 200


@app.route("/send/<string:module_id>", method=["POST"])
async def send(module_id: str):
    neighbors = network.get(module_id, [])
    body = await request.get_data()

    for neighbor in neighbors:
        if neighbor in module_id_map.keys():
            neighbor_url = f"http://{module_id_map[neighbor]}:{MODULE_PORT}/receive"

            async with AsyncClient() as client:
                await client.post(neighbor_url, content=body)

    return jsonify({"status": "message sent", "module_id": module_id}), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=getenv("NETWORK_PORT", 8000),
        debug=True
    )
