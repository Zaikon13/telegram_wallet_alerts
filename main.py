import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LAST_TX_HASH = None
API_URL = f"https://cronos.org/explorer/api?module=account&action=txlist&address={WALLET_ADDRESS}"

def get_latest_transaction():
    try:
        response = requests.get(API_URL)
        data = response.json()
        if "result" in data and isinstance(data["result"], list) and len(data["result"]) > 0:
            return data["result"][0]  # Latest tx
        else:
            return None
    except Exception as e:
        print("Error fetching transaction:", e)
        return None

def send_telegram_alert(message):
    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        requests.post(telegram_url, data=payload)
    except Exception as e:
        print("Error sending Telegram alert:", e)

def monitor_wallet():
    global LAST_TX_HASH
    while True:
        tx = get_latest_transaction()
        if tx and isinstance(tx, dict):
            tx_hash = tx.get("hash")
            if tx_hash and tx_hash != LAST_TX_HASH:
                from_address = tx.get("from")
                to_address = tx.get("to")
                value = tx.get("value")
                message = f"📥 New transaction detected:\nHash: {tx_hash}\nFrom: {from_address}\nTo: {to_address}\nValue: {value}"
                send_telegram_alert(message)
                LAST_TX_HASH = tx_hash
        time.sleep(10)

if __name__ == "__main__":
    monitor_wallet()
