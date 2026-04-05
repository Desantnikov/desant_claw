from qdrant_client.http.models import UpdateResult

from services.vector.email.chunker import Chunker
from services.vector.email.models import EmailChunk
from src.embedding_models.bge_m3 import initialize_model
from src.storage.qdrant.repositories.email_repository import QdrantEmailRepository
from src.storage.qdrant.client import get_async_qdrant_client_singleton


class EmailVectorizationService:
    def __init__(self):
        self.embedding_model = initialize_model()
        self.chunker = Chunker()
        self.qdrant_email_repository = QdrantEmailRepository(client=get_async_qdrant_client_singleton())


    async def upsert_email(self, email_data: dict):
        email_chunks = await self.chunk_and_vectorize_email(email_data)
        upsert_result = await self.qdrant_email_repository.upsert_email_chunks(email_chunks)

        return upsert_result

    async def upsert_email_chunks_bulk(self, email_chunks: list[EmailChunk]) -> UpdateResult:
        return await self.qdrant_email_repository.upsert_email_chunks(email_chunks)

    async def chunk_and_vectorize_email(self, email_data) -> list[EmailChunk]:
        chunks = self.chunker.chunk_email(email_data=email_data)
        for chunk in chunks:
            vectorized_chunk = self.embedding_model.encode(chunk.as_text())
            chunk.dense_vector = vectorized_chunk['dense_vecs']
        return chunks