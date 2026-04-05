from .models import EmailChunk


class Chunker:
    # def __init__(self, email) -> None:
    #     self.email = email

    WORDS_PER_CHUNK_AMOUNT = 120
    OVERLAP_WORDS = 30

    def chunk_email(self, email_data) -> list[EmailChunk]:
        external_message_id = email_data["external_message_id"]
        subject = email_data['subject']
        sender = email_data['sender']

        email_body = email_data['body_text']
        email_words = email_body.split()

        chunks_amount = len(email_words) // self.WORDS_PER_CHUNK_AMOUNT

        chunk_instances = []
        for chunk_index in range(chunks_amount):
            chunk_start = chunk_index * self.WORDS_PER_CHUNK_AMOUNT

            if chunk_index > 0:
                chunk_start = chunk_start - self.OVERLAP_WORDS

            chunk_end = chunk_start + self.WORDS_PER_CHUNK_AMOUNT

            chunk_words = email_words[chunk_start:chunk_end]

            chunk_text = ' '.join(chunk_words)

            chunk_instance = EmailChunk(
                external_message_id=external_message_id,
                sender=sender,
                subject=subject,
                chunk_text=chunk_text,
                chunk_index=chunk_index,
            )
            chunk_instances.append(chunk_instance)


        return chunk_instances