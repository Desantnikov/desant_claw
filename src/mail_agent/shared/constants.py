import os

INTERNAL_EMAIL_ADDRESS = os.environ.get("INTERNAL_EMAIL_ADDRESS")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gpt-5.1")