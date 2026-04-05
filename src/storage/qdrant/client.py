from qdrant_client import AsyncQdrantClient

from src.settings import settings


_client: AsyncQdrantClient | None = None

def get_async_qdrant_client_singleton() -> AsyncQdrantClient:
    """ Return singleton AsyncQdrantClient instance."""
    global _client

    if _client is None:
        _client = AsyncQdrantClient(
            location=settings.QDRANT_HOST,
            port=settings.QDRANT_REST_PORT,
            grpc_port=settings.QDRANT_GRPC_PORT,
            prefer_grpc=settings.QDRANT_PREFER_GRPC,
            timeout=settings.QDRANT_CLIENT_TIMEOUT,
        )

    return _client
