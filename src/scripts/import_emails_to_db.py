import asyncio
import base64
import logging
import os
from datetime import datetime, timedelta, timezone
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from typing import Any
from uuid import uuid4

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.storage.postgres.models.email import Email


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =========================
# Settings
# =========================

DATABASE_URL = os.environ["DATABASE_URL"]
GOOGLE_OAUTH_TOKEN_FILE = os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", "token.json")
GMAIL_QUERY = os.environ.get("GMAIL_QUERY", "in:inbox")
GMAIL_PAGE_SIZE = int(os.environ.get("GMAIL_PAGE_SIZE", "500"))
GMAIL_FETCH_BATCH_SIZE = int(os.environ.get("GMAIL_FETCH_BATCH_SIZE", "100"))
GMAIL_OLDER_OVERLAP_DAYS = int(os.environ.get("GMAIL_OLDER_OVERLAP_DAYS", "1"))


def build_sqlalchemy_database_url(database_url: str) -> str:
    # Convert DSN to SQLAlchemy DSN for async psycopg
    if database_url.startswith("postgresql+psycopg://"):
        return database_url

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    raise ValueError(f"Unsupported DATABASE_URL format: {database_url}")


SQLALCHEMY_DATABASE_URL = build_sqlalchemy_database_url(DATABASE_URL)


# =========================
# Gmail helpers
# =========================

def load_google_credentials() -> Credentials:
    # Load OAuth credentials from token file
    credentials = Credentials.from_authorized_user_file(
        GOOGLE_OAUTH_TOKEN_FILE,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    return credentials


def build_gmail_service():
    credentials = load_google_credentials()
    return build("gmail", "v1", credentials=credentials)


def decode_mime_header(value: str | None) -> str | None:
    # Decode MIME-encoded headers like =?UTF-8?B?...?=
    if value is None:
        return None

    try:
        return str(make_header(decode_header(value)))
    except Exception as error:
        logger.warning("Failed to decode MIME header: %s | error=%s", value, error)
        return value


def extract_plain_text_body(email_message) -> str | None:
    # Prefer text/plain parts and skip attachments
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if content_type == "text/plain" and "attachment" not in content_disposition.lower():
                try:
                    return part.get_content()
                except Exception as error:
                    logger.debug("Failed to extract text/plain part: %s", error)
                    continue

        return None

    try:
        return email_message.get_content()
    except Exception as error:
        logger.debug("Failed to extract non-multipart text body: %s", error)
        return None


def extract_html_body(email_message) -> str | None:
    # Extract text/html part if present
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if content_type == "text/html" and "attachment" not in content_disposition.lower():
                try:
                    return part.get_content()
                except Exception as error:
                    logger.debug("Failed to extract text/html part: %s", error)
                    continue

        return None

    if email_message.get_content_type() == "text/html":
        try:
            return email_message.get_content()
        except Exception as error:
            logger.debug("Failed to extract html body: %s", error)
            return None

    return None


def detect_has_attachments(email_message) -> bool:
    # Detect attachment parts
    if not email_message.is_multipart():
        return False

    for part in email_message.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        if "attachment" in content_disposition.lower():
            return True

    return False


def safe_base64_url_decode(raw_value: str) -> bytes:
    # Gmail raw payload may omit padding
    padding = "=" * (-len(raw_value) % 4)
    return base64.urlsafe_b64decode(raw_value + padding)


def parse_gmail_raw_message(raw_message: dict[str, Any]) -> dict[str, Any]:
    # Parse Gmail raw message into Email model payload
    raw_encoded_message = raw_message["raw"]
    raw_bytes = safe_base64_url_decode(raw_encoded_message)
    parsed_message = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    subject = decode_mime_header(parsed_message.get("Subject"))
    sender = decode_mime_header(parsed_message.get("From"))
    recipients = decode_mime_header(parsed_message.get("To"))

    body_text = extract_plain_text_body(parsed_message)
    body_html = extract_html_body(parsed_message)
    body_cleaned = body_text

    sent_at_header = parsed_message.get("Date")
    sent_at = None
    if sent_at_header:
        try:
            sent_at = parsedate_to_datetime(sent_at_header)
        except Exception as error:
            logger.debug("Failed to parse Date header '%s': %s", sent_at_header, error)

    return {
        "id": str(uuid4()),
        "external_message_id": raw_message.get("id"),
        "external_thread_id": raw_message.get("threadId"),
        "subject": subject,
        "sender": sender,
        "recipients": recipients,
        "body_text": body_text,
        "body_html": body_html,
        "body_cleaned": body_cleaned,
        "sent_at": sent_at,
        "has_attachments": detect_has_attachments(parsed_message),
    }


def fetch_message_refs_page(
    gmail_service,
    query: str,
    page_size: int,
    page_token: str | None,
) -> dict[str, Any]:
    # Fetch one page of Gmail message refs
    return (
        gmail_service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=page_size,
            pageToken=page_token,
        )
        .execute()
    )


def fetch_raw_message(gmail_service, message_id: str) -> dict[str, Any]:
    # Fetch raw RFC 2822 message
    return (
        gmail_service.users()
        .messages()
        .get(userId="me", id=message_id, format="raw")
        .execute()
    )


def chunk_list(items: list[Any], batch_size: int) -> list[list[Any]]:
    # Split list into chunks
    return [
        items[start_index:start_index + batch_size]
        for start_index in range(0, len(items), batch_size)
    ]


# =========================
# DB helpers
# =========================

async def get_oldest_imported_sent_at(session: AsyncSession) -> datetime | None:
    # Read oldest imported sent_at to continue importing older emails
    statement = select(func.min(Email.sent_at))
    result = await session.execute(statement)
    return result.scalar_one_or_none()


def build_older_backfill_gmail_query(
    base_query: str,
    oldest_imported_sent_at: datetime | None,
) -> str:
    # Limit Gmail search to emails older than the oldest already imported one.
    # Add a small overlap because Gmail before: works by date, not exact timestamp.
    if oldest_imported_sent_at is None:
        return base_query

    normalized_datetime = oldest_imported_sent_at
    if normalized_datetime.tzinfo is None:
        normalized_datetime = normalized_datetime.replace(tzinfo=timezone.utc)

    overlap_boundary = normalized_datetime + timedelta(days=GMAIL_OLDER_OVERLAP_DAYS)
    gmail_before_value = overlap_boundary.astimezone(timezone.utc).strftime("%Y/%m/%d")

    return f"{base_query} before:{gmail_before_value}"


async def insert_email_batch(
    session: AsyncSession,
    email_payloads: list[dict[str, Any]],
) -> int:
    # Insert batch with ON CONFLICT DO NOTHING to skip duplicates in DB
    if not email_payloads:
        return 0

    insert_statement = pg_insert(Email).values(email_payloads)
    insert_statement = insert_statement.on_conflict_do_nothing(
        index_elements=[Email.external_message_id]
    ).returning(Email.external_message_id)

    result = await session.execute(insert_statement)
    inserted_ids = result.scalars().all()
    return len(inserted_ids)


# =========================
# Main import flow
# =========================

async def import_emails_to_db() -> None:
    logger.info("Starting Gmail -> Postgres import")
    logger.info("Base Gmail query: %s", GMAIL_QUERY)

    gmail_service = build_gmail_service()

    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        future=True,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    total_refs_seen = 0
    total_raw_fetched = 0
    total_created = 0
    total_skipped = 0
    total_duplicate_in_chunk = 0
    total_fetch_errors = 0
    total_parse_errors = 0
    next_page_token: str | None = None
    page_index = 0

    try:
        async with session_factory() as session:
            oldest_imported_sent_at = await get_oldest_imported_sent_at(session)
            effective_gmail_query = build_older_backfill_gmail_query(
                base_query=GMAIL_QUERY,
                oldest_imported_sent_at=oldest_imported_sent_at,
            )

            logger.info("Oldest imported sent_at: %s", oldest_imported_sent_at)
            logger.info("Effective Gmail query: %s", effective_gmail_query)

            while True:
                page_index += 1

                try:
                    page_response = await asyncio.to_thread(
                        fetch_message_refs_page,
                        gmail_service,
                        effective_gmail_query,
                        GMAIL_PAGE_SIZE,
                        next_page_token,
                    )
                except Exception:
                    logger.exception("Failed to fetch Gmail page: page_index=%d", page_index)
                    break

                message_refs = page_response.get("messages", [])
                next_page_token = page_response.get("nextPageToken")

                if not message_refs:
                    logger.info("No more message refs returned. Stopping.")
                    break

                total_refs_seen += len(message_refs)
                logger.info(
                    "Fetched Gmail page: page_index=%d page_size=%d total_refs_seen=%d",
                    page_index,
                    len(message_refs),
                    total_refs_seen,
                )

                for chunk_index, message_ref_chunk in enumerate(
                    chunk_list(message_refs, GMAIL_FETCH_BATCH_SIZE),
                    start=1,
                ):
                    logger.info(
                        "Processing chunk: page_index=%d chunk_index=%d chunk_size=%d",
                        page_index,
                        chunk_index,
                        len(message_ref_chunk),
                    )

                    raw_messages: list[dict[str, Any]] = []

                    # Sequential fetch is slower, but safer for large imports and API limits
                    for message_ref in message_ref_chunk:
                        message_id = message_ref["id"]

                        try:
                            raw_message = await asyncio.to_thread(
                                fetch_raw_message,
                                gmail_service,
                                message_id,
                            )
                            raw_messages.append(raw_message)
                            total_raw_fetched += 1
                        except Exception:
                            total_fetch_errors += 1
                            logger.exception(
                                "Failed to fetch raw Gmail message: message_id=%s",
                                message_id,
                            )

                    if not raw_messages:
                        logger.warning(
                            "Chunk has no fetched raw messages: page_index=%d chunk_index=%d",
                            page_index,
                            chunk_index,
                        )
                        continue

                    parsed_payloads: list[dict[str, Any]] = []

                    for raw_message in raw_messages:
                        try:
                            email_payload = parse_gmail_raw_message(raw_message)

                            if not email_payload["external_message_id"]:
                                total_skipped += 1
                                logger.warning("Skipping email without external_message_id")
                                continue

                            if not email_payload["sender"]:
                                total_skipped += 1
                                logger.warning(
                                    "Skipping email without sender: external_message_id=%s",
                                    email_payload["external_message_id"],
                                )
                                continue

                            parsed_payloads.append(email_payload)

                        except Exception:
                            total_parse_errors += 1
                            total_skipped += 1
                            logger.exception(
                                "Failed to parse raw Gmail message: external_message_id=%s",
                                raw_message.get("id"),
                            )

                    if not parsed_payloads:
                        logger.info(
                            "No parsed payloads left after validation: page_index=%d chunk_index=%d",
                            page_index,
                            chunk_index,
                        )
                        continue

                    unique_payloads: list[dict[str, Any]] = []
                    seen_external_message_ids: set[str] = set()

                    for email_payload in parsed_payloads:
                        external_message_id = email_payload["external_message_id"]

                        if external_message_id in seen_external_message_ids:
                            total_duplicate_in_chunk += 1
                            continue

                        seen_external_message_ids.add(external_message_id)
                        unique_payloads.append(email_payload)

                    try:
                        inserted_count = await insert_email_batch(
                            session=session,
                            email_payloads=unique_payloads,
                        )
                        await session.commit()
                        total_created += inserted_count

                        logger.info(
                            "Committed chunk: page_index=%d chunk_index=%d inserted=%d skipped_as_duplicates=%d total_created=%d",
                            page_index,
                            chunk_index,
                            inserted_count,
                            len(unique_payloads) - inserted_count,
                            total_created,
                        )
                    except Exception:
                        await session.rollback()
                        logger.exception(
                            "Failed to insert chunk, rolled back only current chunk: page_index=%d chunk_index=%d",
                            page_index,
                            chunk_index,
                        )

                if not next_page_token:
                    logger.info("No next page token left. Import finished.")
                    break

        logger.info(
            "Import finished: refs_seen=%d raw_fetched=%d created=%d skipped=%d duplicate_in_chunk=%d fetch_errors=%d parse_errors=%d",
            total_refs_seen,
            total_raw_fetched,
            total_created,
            total_skipped,
            total_duplicate_in_chunk,
            total_fetch_errors,
            total_parse_errors,
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(import_emails_to_db())