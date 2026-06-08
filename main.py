import asyncio

from src.mail_agent.services.fetch_email_service import FetchEmailService
from src.mail_agent.runtime.graph_runtime import GraphRuntime
from src.mail_agent.runtime.event_factory import EventFactory


if __name__ == "__main__":
    mail_service = FetchEmailService()

    # latest_mail = mail_service.get_latest_email()

    # Synthetic sample message used for local runs. Use placeholder data only.
    latest_mail = {'id': 'demo-0001', 'threadId': 'demo-thread-0001',
                   'snippet': 'Read the file notes.txt and send it back to me',
                   'body': 'Read file "notes.txt" and send it back to me\r\n', 'subject': 'Instructions',
                   'sender': 'Demo User <demo@example.com>'}

    # Sample human-in-the-loop response message. The snippet carries the thread id to resume.
    approve_latest_mail = {'id': 'demo-0001', 'threadId': 'demo-thread-0001',
                   'snippet': '00000000-0000-0000-0000-000000000000',
                   'body': 'Read file "notes.txt" and send it back to me\r\n', 'subject': 'HITL_RESPONSE',
                   'sender': 'Demo User <demo@example.com>'}

    event = EventFactory.from_email(raw_email_data=latest_mail)
    # event = EventFactory.from_email(raw_email_data=approve_latest_mail)
    graph_runtime = GraphRuntime()
    event.decisions = [{"type": "approve"}]
    result = asyncio.run(graph_runtime.process_event(event=event))

    print(f'Result: {result}')
