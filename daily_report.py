import requests
import datetime
import os

# 環境変数から API キーと Discord Webhook URL を取得
POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 監視対象のウォレットアドレス
WALLET_ADDRESS = "0xe7ee1d51f58a450552ff45c37630335d534ce9e3"
SNPT_CONTRACT = "0x22737f5bbb7c5b5ba407b0c1c9a9cdf66cf25d7d"

# JST基準の前日の日付を取得
jst_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)  # JSTの現在時刻
yesterday_jst = jst_now.date() - datetime.timedelta(days=1)  # JSTの前日の日付

# JST 0:00 ～ JST 23:59 を UTCに変換
start_timestamp = int((datetime.datetime(yesterday_jst.year, yesterday_jst.month, yesterday_jst.day, 0, 0) - datetime.timedelta(hours=9)).timestamp())  # JST 0:00 (UTC前日15:00)
end_timestamp = int((datetime.datetime(yesterday_jst.year, yesterday_jst.month, yesterday_jst.day, 23, 59, 59) - datetime.timedelta(hours=9)).timestamp())  # JST 23:59 (UTC当日14:59)

# PolygonScan API でトランザクション取得
url = f"https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={SNPT_CONTRACT}&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=desc&apikey={POLYGONSCAN_API_KEY}"
response = requests.get(url).json()

# IN/OUT の集計
total_in = 0
total_out = 0

for tx in response.get("result", []):
    timestamp = int(tx["timeStamp"])  # トランザクションの UNIX 時間
    value = int(tx["value"]) / (10**18)  # SNPT の小数点調整

    if start_timestamp <= timestamp <= end_timestamp:
        if tx["to"].lower() == WALLET_ADDRESS.lower():
            total_in += value  # 受け取った額
        elif tx["from"].lower() == WALLET_ADDRESS.lower():
            total_out += value  # 送った額

# 差し引き計算
net_snpt = total_in - total_out

# Discord へ送信
message = f"""
📢 **{yesterday_jst} (JST) の SNPT 合計**
🟢 **IN:** {total_in:.4f} SNPT
🔴 **OUT:** {total_out:.4f} SNPT
⚖️ **Net (IN - OUT):** {net_snpt:.4f} SNPT
"""

requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

print("✅ JST基準の前日の SNPT 合計を Discord に送信しました！")
