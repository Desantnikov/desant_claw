from tqdm import tqdm
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct, UpdateResult

from services.vector.email.models import EmailChunk


class QdrantEmailRepository:
    COLLECTION_NAME = "emails"

    def __init__(self, client: AsyncQdrantClient):
        self._client = client

    async def upsert_email_chunks(self, email_chunks: list[EmailChunk]) -> UpdateResult:
        qdrant_points = []
        for email_chunk in tqdm(email_chunks):
            qdrant_point = PointStruct(
                id=email_chunk.qdrant_point_uuid,
                payload=email_chunk.as_qdrant_payload(),
                vector=email_chunk.dense_vector,
            )
            qdrant_points.append(qdrant_point)

        result = await self._client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=qdrant_points
        )


        return result