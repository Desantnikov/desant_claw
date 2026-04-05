from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, Boolean, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.postgres.models.base import Base


class Email(Base):
    __tablename__ = "emails"
    __table_args__ = (
        UniqueConstraint("external_message_id", name="uq_emails_external_message_id"),
        Index("ix_emails_external_thread_id", "external_thread_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # external ids
    external_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    subject: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    sender: Mapped[str] = mapped_column(String(320), nullable=False)

    recipients: Mapped[str | None] = mapped_column(Text, nullable=True)

    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    body_cleaned: Mapped[str | None] = mapped_column(Text, nullable=True)

    # metadata
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)

    # system
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )