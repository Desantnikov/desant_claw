import asyncio

from qdrant_client.models import Distance, VectorParams

from src.embedding_models.bge_m3 import VECTOR_LENGTH
from src.storage.qdrant.client import get_async_qdrant_client_singleton


COLLECTIONS_TO_CREATE = ["emails"]


async def main():
    qdrant_client = get_async_qdrant_client_singleton()

    for collection_name in COLLECTIONS_TO_CREATE:
        existing_collection = await qdrant_client.get_collection(collection_name)

        if existing_collection:
            print(f"Collection {collection_name} already exists")
            continue

        # TODO: add payload indexes and sparse vectors
        collection = await qdrant_client.create_collection(
            collection_name="emails",
            vectors_config=VectorParams(size=VECTOR_LENGTH, distance=Distance.COSINE)
        )
        print(f"Collection {collection_name} created")


if __name__ == "__main__":
    asyncio.run(main())