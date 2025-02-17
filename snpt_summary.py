import requests
import datetime
import os
import time

# 環境変数から API キーと Discord Webhook URL を取得
POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 監視対象のウォレットアドレス
WALLET_ADDRESS = "0xe7ee1d51f58a450552ff45c37630335d534ce9e3"
SNPT_CONTRACT = "0x22737f5bbb7c5b5ba407b0c1c9a9cdf66cf25d7d"

# JST タイムゾーン（UTC+9）
JST = datetime.timezone(datetime.timedelta(hours=9))

# 現在時刻（JST基準）
now_jst = datetime.datetime.now(JST)

# 集計対象の時間帯を決定（JST基準）
hour = now_jst.hour
if 6 <= hour < 12:
    start_time = now_jst.replace(hour=0, minute=0, second=0, microsecond=0)
elif 12 <= hour < 18:
    start_time = now_jst.replace(hour=6, minute=0, second=0, microsecond=0)
elif 18 <= hour < 24:
    start_time = now_jst.replace(hour=12, minute=0, second=0, microsecond=0)
else:
    start_time = now_jst.replace(hour=18, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)

end_time = start_time + datetime.timedelta(hours=6)

# タイムスタンプに変換（UNIX時間）
start_timestamp = int(start_time.timestamp())
end_timestamp = int(end_time.timestamp())

print(f"🕒 集計対象: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ～ {end_time.strftime('%Y-%m-%d %H:%M:%S')} (JST)")

# PolygonScan API でトランザクション取得
url = f"https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={SNPT_CONTRACT}&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=desc&apikey={POLYGONSCAN_API_KEY}"
response = requests.get(url).json()

# IN/OUT の集計
total_in = 0
total_out = 0

for tx in response.get("result", []):
    timestamp = int(tx["timeStamp"])  # UNIX時間
    value = int(tx["value"]) / (10**18)  # 小数点調整

    # タイムスタンプの範囲確認
    if start_timestamp <= timestamp < end_timestamp:
        if tx["to"].lower() == WALLET_ADDRESS.lower():
            total_in += value
        elif tx["from"].lower() == WALLET_ADDRESS.lower():
            total_out += value

# **IN - OUT の差額を計算**
net_balance = total_in - total_out

# Discord へ送信
message = f"""
📢 **{start_time.strftime('%Y-%m-%d %H:%M:%S')} ～ {end_time.strftime('%Y-%m-%d %H:%M:%S')} (JST) の SNPT 小計**
🟢 **IN:** {total_in:.4f} SNPT
🔴 **OUT:** {total_out:.4f} SNPT
💰 **NET (IN - OUT):** {net_balance:.4f} SNPT
"""

requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

print("✅ 指定時間帯の SNPT 小計を Discord に送信しました！")
