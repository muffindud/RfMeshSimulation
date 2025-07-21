from os import getenv
from random import randint, sample

from quart import Quart, request, jsonify
from httpx import AsyncClient


NEIGHBORS = "neighbors"
DISTANCE = "distance"

MODULE_PORT = getenv("MODULE_PORT", 5000)
BRANCHING_FACTOR = (1, 3)

app = Quart(__name__)

# Each key is a node ID, and the value is a list of neighbor node IDs.
network: dict[str, dict[str, int | set]] = {}

# Each key is a module ID, and the value is the IP address of the module.
module_id_map: dict[str, str] = {}

modules_with_neighbors: list[str] = []

# Global variable to store the manager ID
manager_id: str | None = None


# Create a two-way link between nodes
def link(module_id: str, neighbor_id: str) -> None:
    if neighbor_id != module_id:
        print(f"Link: {module_id} and {neighbor_id}")
        network[module_id][NEIGHBORS].add(neighbor_id)
        network[neighbor_id][NEIGHBORS].add(module_id)


def create_random_links(module_id: str) -> None:
    if len(network) == 1:
        network[module_id][DISTANCE] = 0
        modules_with_neighbors.append(module_id)
        return

    elif BRANCHING_FACTOR[0] >= len(network) - 1:
        for node in modules_with_neighbors:
            link(module_id, node)

        network[module_id][DISTANCE] = get_distance(module_id)
        modules_with_neighbors.append(module_id)

    elif BRANCHING_FACTOR[1] > len(network) - 1:
        branch_count = randint(BRANCHING_FACTOR[0], len(network) - 1)
        nodes = sample(modules_with_neighbors, branch_count)

        for node in nodes:
            link(module_id, node)

        network[module_id][DISTANCE] = get_distance(module_id)
        modules_with_neighbors.append(module_id)

    else:
        branch_count = randint(*BRANCHING_FACTOR)

        nodes = sample(modules_with_neighbors, branch_count)

        for node in nodes:
            link(module_id, node)

        network[module_id][DISTANCE] = get_distance(module_id)
        modules_with_neighbors.append(module_id)


def get_distance(module_id: str) -> int:
    min_distance = float("inf")

    for neighbor_id in network.get(module_id).get(NEIGHBORS):
        if neighbor_id != module_id:
            min_distance = network.get(neighbor_id).get(DISTANCE) if min_distance > network.get(neighbor_id).get(DISTANCE) else min_distance

    return min_distance + 1 if min_distance != float("inf") else 0


@app.route("/subscribe/worker/<string:module_id>", methods=["POST"])
async def subscribe_worker(module_id: str):
    print(f"Received worker subscribe {module_id} {request.remote_addr}")

    network[module_id] = {}
    network[module_id][NEIGHBORS] = set()
    module_id_map[module_id] = request.remote_addr
    create_random_links(module_id)

    return "", 204


@app.route("/subscribe/manager/<string:module_id>", methods=["POST"])
async def subscribe_manager(module_id: str):
    print(f"Received manager subscribe {module_id} {request.remote_addr}")

    network[module_id] = {}
    network[module_id][NEIGHBORS] = set()
    module_id_map[module_id] = request.remote_addr
    global manager_id
    manager_id = module_id
    create_random_links(module_id)

    return jsonify({"distance": get_distance(module_id)}), 200


@app.route("/send/<string:module_id>", methods=["POST"])
async def send(module_id: str):
    neighbors = network.get(module_id, [])
    body = await request.get_data()

    print(f"Received packet from {request.remote_addr}")

    for neighbor_id in neighbors:
        if neighbor_id in module_id_map.keys():
            neighbor_url = f"http://{module_id_map.get(neighbor_id)}:{MODULE_PORT}/receive"

            async with AsyncClient() as client:
                print(f"Redirected packet to {neighbor_url}")
                await client.post(neighbor_url, content=body)

    return "", 204


@app.route("/network", methods=["GET"])
async def get_network():
    return str(network), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=getenv("NETWORK_PORT", 4000),
        debug=True
    )
