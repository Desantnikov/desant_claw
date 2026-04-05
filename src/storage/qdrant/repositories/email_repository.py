from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct

from services.vector.email.models import EmailChunk


class EmailRepository:
    COLLECTION_NAME = "emails"

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def upsert_email(self, email_chunks: list[EmailChunk]):
        qdrant_points = []
        for email_chunk in email_chunks:
            qdrant_point = PointStruct(
                id=f"{email_chunk.external_message_id}_{email_chunk.chunk_index}",
                payload=email_chunk.as_qdrant_payload(),
                vector={
                    "dense": email_chunk.vector,
                },
            )
            qdrant_points.append(qdrant_point)

        result = await self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=qdrant_points
        )