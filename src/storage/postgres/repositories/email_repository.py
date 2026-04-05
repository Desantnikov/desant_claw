from collections.abc import Sequence

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.postgres.models.email import Email


class EmailRepository:
    def __init__(self, session: AsyncSession):
        # Session is injected from outside as well as commit should happen outside
        self._session = session

    async def create(
        self,
        *,
        external_message_id: str | None,
        external_thread_id: str | None,
        subject: str | None,
        sender: str,
        recipients: str | None,
        body_text: str | None,
        body_html: str | None,
        body_cleaned: str | None,
    ) -> Email:
        email = Email(
            external_message_id=external_message_id,
            external_thread_id=external_thread_id,
            subject=subject,
            sender=sender,
            recipients=recipients,
            body_text=body_text,
            body_html=body_html,
            body_cleaned=body_cleaned,
        )

        self._session.add(email)
        await self._session.flush()
        return email

    async def bulk_create(self, email_payloads: list[dict]) -> None:
        # Add many ORM objects in one batch
        email_models = [Email(**email_payload) for email_payload in email_payloads]
        self._session.add_all(email_models)
        await self._session.flush()

    async def get_by_external_message_id(self, external_message_id: str) -> Email | None:
        statement = select(Email).where(Email.external_message_id == external_message_id)
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def get_existing_external_message_ids(
        self,
        external_message_ids: Sequence[str],
    ) -> set[str]:
        if not external_message_ids:
            return set()

        statement = select(Email.external_message_id).where(
            Email.external_message_id.in_(external_message_ids)
        )
        result = await self._session.execute(statement)
        existing_ids = result.scalars().all()

        # Filter possible None just in case
        return {existing_id for existing_id in existing_ids if existing_id is not None}

    async def list_recent(self, *, limit: int = 20) -> Sequence[Email]:
        statement = (
            select(Email)
            .order_by(Email.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def list_by_sender(self, *, sender: str, limit: int = 50) -> Sequence[Email]:
        statement = (
            select(Email)
            .where(Email.sender == sender)
            .order_by(Email.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def list_by_external_thread_id(
        self,
        *,
        external_thread_id: str,
        limit: int = 100,
    ) -> Sequence[Email]:
        statement = (
            select(Email)
            .where(Email.external_thread_id == external_thread_id)
            .order_by(Email.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def update_body_cleaned(
        self,
        *,
        email_id: str,
        body_cleaned: str,
    ) -> None:
        statement = (
            update(Email)
            .where(Email.id == email_id)
            .values(body_cleaned=body_cleaned)
        )
        await self._session.execute(statement)

    async def delete(self, email_id: str) -> None:
        statement = delete(Email).where(Email.id == email_id)
        await self._session.execute(statement)