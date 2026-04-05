import argparse
import asyncio
from typing import Any

from tqdm import tqdm

from src.services.vector.email.service import EmailVectorizationService
from src.storage.postgres.repositories.email_repository import EmailRepository
from src.storage.postgres.session import SessionFactory


DEFAULT_TOTAL_EMAILS = 50_000
DEFAULT_BATCH_SIZE = 100


async def fetch_email_batch(
    batch_size: int,
    batch_index: int,
) -> list[dict[str, Any]]:
    offset = batch_index * batch_size

    async with SessionFactory() as session:
        email_repository = EmailRepository(session=session)
        query_result = await email_repository.get_emails(limit=batch_size, offset=offset)
        raw_rows = query_result.all()

    # Assumption:
    # get_emails() returns rows where the ORM entity is the first element.
    return [raw_row[0].__dict__ for raw_row in raw_rows]


async def process_batch(
    email_vectorization_service: EmailVectorizationService,
    email_batch: list[dict[str, Any]],
    batch_index: int,
) -> tuple[int, int]:
    email_chunks = []

    for email_data in tqdm(email_batch, desc=f"Batch {batch_index}", leave=False):
        chunks = await email_vectorization_service.chunk_and_vectorize_email(email_data=email_data)
        email_chunks.extend(chunks)

    print(
        f"[Batch {batch_index}] "
        f"Fetched {len(email_batch)} emails, created {len(email_chunks)} chunks"
    )

    if not email_chunks:
        print(f"[Batch {batch_index}] No chunks to upsert")
        return len(email_batch), 0

    from itertools import islice

    def batched(items: list, batch_size: int):
        iterator = iter(items)
        while batch := list(islice(iterator, batch_size)):
            yield batch

    for qdrant_batch_index, chunk_batch in enumerate(batched(email_chunks, 200)):
        print(
            f"[Email batch {batch_index}] "
            f"Qdrant sub-batch {qdrant_batch_index}, points={len(chunk_batch)}"
        )
        await email_vectorization_service.upsert_email_chunks_bulk(email_chunks=chunk_batch)

    print(
        f"[Batch {batch_index}] "
        f"Upserted {len(email_chunks)} chunks"
    )

    return len(email_batch), len(email_chunks)


async def main(
    total_emails: int,
    batch_size: int,
    start_batch_index: int,
) -> None:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")

    if total_emails <= 0:
        raise ValueError("total_emails must be greater than 0")

    if start_batch_index < 0:
        raise ValueError("start_batch_index must be >= 0")

    email_vectorization_service = EmailVectorizationService()

    total_batches = (total_emails + batch_size - 1) // batch_size

    if start_batch_index >= total_batches:
        print(
            f"start_batch_index={start_batch_index} is out of range. "
            f"Total batches: {total_batches}"
        )
        return

    total_processed_emails = 0
    total_upserted_chunks = 0

    import time
    for batch_index in range(start_batch_index, total_batches):
        time.sleep(1)
        current_offset = batch_index * batch_size
        remaining_emails = total_emails - current_offset

        if remaining_emails <= 0:
            break

        current_batch_size = min(batch_size, remaining_emails)

        print(
            f"\n=== Processing batch {batch_index}/{total_batches - 1} "
            f"(offset={current_offset}, batch_size={current_batch_size}) ==="
        )

        email_batch = await fetch_email_batch(
            batch_size=current_batch_size,
            batch_index=batch_index,
        )

        if not email_batch:
            print(
                f"[Batch {batch_index}] No emails returned from DB. "
                f"Stopping early."
            )
            break

        processed_emails_count, upserted_chunks_count = await process_batch(
            email_vectorization_service=email_vectorization_service,
            email_batch=email_batch,
            batch_index=batch_index,
        )

        total_processed_emails += processed_emails_count
        total_upserted_chunks += upserted_chunks_count

        print(
            f"[Batch {batch_index}] Done. "
            f"Total processed emails so far: {total_processed_emails}. "
            f"Total upserted chunks so far: {total_upserted_chunks}"
        )

    print("\n=== Ingestion finished ===")
    print(f"Total processed emails: {total_processed_emails}")
    print(f"Total upserted chunks: {total_upserted_chunks}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch email ingestion into vector storage"
    )
    parser.add_argument(
        "--total-emails",
        type=int,
        default=DEFAULT_TOTAL_EMAILS,
        help=f"How many emails to ingest in total. Default: {DEFAULT_TOTAL_EMAILS}",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"How many emails to process per batch. Default: {DEFAULT_BATCH_SIZE}",
    )
    parser.add_argument(
        "--start-batch-index",
        type=int,
        default=0,
        help="Batch index to start from, useful for resume. Default: 0",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    asyncio.run(
        main(
            total_emails=arguments.total_emails,
            batch_size=arguments.batch_size,
            start_batch_index=arguments.start_batch_index,
        )
    )