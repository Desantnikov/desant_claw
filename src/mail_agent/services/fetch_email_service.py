from langchain_google_community import GmailToolkit


class FetchEmailService:
    def __init__(self):
        toolkit = GmailToolkit()
        tools = {tool.name: tool for tool in toolkit.get_tools()}
        self.search = tools["search_gmail"]
        self.get_message = tools["get_gmail_message"]

    def get_latest_email(self):
        # Search for the newest email in inbox
        search_result = self.search.invoke({"query": "in:inbox", "max_results": 1})

        if not search_result:
            return None

        message_id = search_result[0]["id"]
        return self.get_message.invoke({"message_id": message_id})

    async def get_all_emails(self, query: str = "in:inbox", max_results: int = 1000) -> list[dict]:
        # Search for email message ids
        search_result = await self.search.ainvoke({"query": query, "max_results": max_results})

        if not search_result:
            return []

        emails: list[dict] = []

        for email_info in search_result:
            message_id = email_info["id"]
            full_message = await self.get_message.ainvoke({"message_id": message_id})
            emails.append(full_message)

        return emails
