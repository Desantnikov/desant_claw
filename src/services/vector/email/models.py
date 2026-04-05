import uuid
from typing import Any

from pydantic import BaseModel


class EmailChunk(BaseModel):
    external_message_id: str
    sender: str
    subject: str

    chunk_text: str
    chunk_index: int

    dense_vector: Any | None = None

    @property
    def qdrant_point_uuid(self) -> str:
        """ Generate a deterministic uuid to be used as a point id in qdrant """
        raw_value = f"{self.external_message_id}:{self.chunk_index}"
        namespace = uuid.NAMESPACE_URL
        return str(uuid.uuid5(namespace, raw_value))

    def as_text(self):
        return f"Sender: {self.sender}; Subject: {self.subject}; Text: {self.chunk_text}"

    def as_qdrant_payload(self):
        return {"external_message_id": self.external_message_id, "chunk_index": self.chunk_index, "chunk_text": self.chunk_text}