import requests

from utils.get_secrets import get_secrets

TELEGRAM_TOKEN = get_secrets("GEMINI-AWS")["TELEGRAM_TOKEN"]
TELEGRAM_USER_ID = get_secrets("GEMINI-AWS")["TELEGRAM_USER_ID"]
TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_TOKEN)


def telegram_notification(message):
    try:
        payload = {
            "text": message.encode("utf8"),
            "chat_id": TELEGRAM_USER_ID
        }
        requests.post(TELEGRAM_URL, payload)

    except Exception as e:
        raise e
