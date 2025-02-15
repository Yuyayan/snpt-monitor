import requests
import json
import os

# 監視するウォレットアドレス
WATCH_ADDRESS = "0xe7ee1d51f58a450552ff45c37630335d534ce9e3".lower()
# SNPTのコントラクトアドレス
SNPT_CONTRACT = "0x22737f5bbb7c5b5ba407b0c1c9a9cdf66cf25d7d".lower()
# APIキーとDiscord Webhook URL（環境変数から取得）
POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_transactions():
    url = f"https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={SNPT_CONTRACT}&address={WATCH_ADDRESS}&sort=desc&apikey={POLYGONSCAN_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return []

    data = response.json()
    if data["status"] != "1":
        print("No transactions found")
        return []

    return data["result"]

def send_discord_notification(message):
    payload = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def monitor_transactions():
    transactions = get_transactions()
    if not transactions:
        return

    for tx in transactions[:5]:  # 最新5件をチェック
        from_address = tx["from"].lower()
        to_address = tx["to"].lower()
        value = int(tx["value"]) / (10 ** int(tx["tokenDecimal"]))  # トークンの桁数を調整
        hash_link = f"https://polygonscan.com/tx/{tx['hash']}"

        # ① ウォレット**への**送金
        if to_address == WATCH_ADDRESS:
            message = f"💰 **SNPT受取** 💰\nウォレットに {value} SNPT 受け取り！\n詳細: {hash_link}"
            send_discord_notification(message)

        # ② ウォレット**から**送金
        elif from_address == WATCH_ADDRESS:
            message = f"📤 **SNPT送金** 📤\nウォレットから {value} SNPT 送金！\n詳細: {hash_link}"
            send_discord_notification(message)

if __name__ == "__main__":
    monitor_transactions()
