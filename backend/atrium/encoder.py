import base64
import json


class Encoder:
    def encode(self, message: dict) -> str:
        raw = json.dumps(message, separators=(",", ":")).encode("utf-8")
        return base64.b64encode(raw).decode("ascii")

    def decode(self, data: str) -> dict:
        raw = base64.b64decode(data.encode("ascii"), validate=True)
        message = json.loads(raw.decode("utf-8"))
        if not isinstance(message, dict):
            raise ValueError("message must be an object")
        return message
