import re


EMAIL_REGEXP = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'


def parse_email(input_string: str):
    parsed_email = re.search(EMAIL_REGEXP, input_string)
    parsed_email = parsed_email.group(0) if parsed_email else None

    if parsed_email is None:
        raise Exception("No email address found")

    return parsed_email
