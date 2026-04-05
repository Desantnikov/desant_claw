from typing import Any

from pydantic import BaseModel


class EmailChunk(BaseModel):
    external_message_id: str
    sender: str
    subject: str

    chunk_text: str
    chunk_index: int

    vector: Any | None = None

    def as_text(self):
        return f"Sender: {self.sender}; Subject: {self.subject}; Text: {self.chunk_text}"

    def as_qdrant_payload(self):
        return {"external_message_id": self.external_message_id, "chunk_index": self.chunk_index}