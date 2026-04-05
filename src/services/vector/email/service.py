from services.vector.email.chunker import Chunker
from services.vector.email.models import EmailChunk
from src.embedding_models.bge_m3 import initialize_model

class EmailVectorizationService:
    def __init__(self):
        self.embedding_model = initialize_model()
        self.chunker = Chunker()

    def vectorize_email(self, email_data) -> list[EmailChunk]:
        chunks = self.chunker.chunk_email(email_data=email_data)

        for chunk in chunks:
            vectorized_chunk = self.embedding_model.encode(chunk.as_text())

            chunk.vector = vectorized_chunk['dense_vecs']

        return chunks