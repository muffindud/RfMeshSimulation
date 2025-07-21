import src.Message
from src.Header import Header


class Message:
    def __init__(
            self,
            header: Header,             # Packet type
            distance: int,              # Hop counts to/from destination
            source_module_id: str,      # Source module ID
            destination_module_id: str, # Destination module ID
            payload_index: int,         # Index of the payload in the payload list§
            payload_count: int,         # Total number of payloads
            payload_size: int,          # Size of the payload in bytes
            payload: bytes,             # Payload data
    ):
        self.header = header
        self.distance = distance
        self.source_module_id = source_module_id
        self.destination_module_id = destination_module_id
        self.payload_index = payload_index
        self.payload_count = payload_count
        self.payload_size = payload_size
        self.payload = payload

    def to_bytes(self) -> bytes:
        ...

    @staticmethod
    def create_message(bin_message: bytes) -> src.Message.Message:
        ...
