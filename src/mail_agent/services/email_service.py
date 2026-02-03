from langchain_google_community import GmailToolkit


class MailService:
    def __init__(self):
        toolkit = GmailToolkit()
        tools = {tool.name: tool for tool in toolkit.get_tools()}
        self.search = tools["search_gmail"]
        self.get_message = tools["get_gmail_message"]

    def get_latest_email(self):
        # Search newest email
        result = self.search.invoke({"query": "in:inbox", "max_results": 1})

        if not result:
            return None

        message_id = result[0]["id"]
        return self.get_message.invoke({"message_id": message_id})