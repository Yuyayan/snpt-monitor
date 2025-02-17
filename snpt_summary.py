import requests
import datetime
import os

# 環境変数から API キーと Discord Webhook URL を取得
POLYGONSCAN_API_KEY = os.getenv("POLYGONSCAN_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 監視対象のウォレットアドレス
WALLET_ADDRESS = "0xe7ee1d51f58a450552ff45c37630335d534ce9e3"
SNPT_CONTRACT = "0x22737f5bbb7c5b5ba407b0c1c9a9cdf66cf25d7d"

# 現在時刻（UTC）
now = datetime.datetime.now(datetime.UTC)

# 6時間前の時刻を計算
start_time = now - datetime.timedelta(hours=6)
start_timestamp = int(start_time.timestamp())  # 6時間前のUNIX時間
end_timestamp = int(now.timestamp())  # 現在のUNIX時間

# PolygonScan API でトランザクション取得
url = f"https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={SNPT_CONTRACT}&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&apikey={POLYGONSCAN_API_KEY}"
response = requests.get(url).json()

# IN/OUT の集計
total_in = 0
total_out = 0

for tx in response.get("result", []):
    timestamp = int(tx["timeStamp"])  # UNIX時間
    raw_value = tx["value"]  # 送金額（文字列）

    try:
        value = int(raw_value) / (10**18)  # 小数点調整
    except ValueError as e:
        print(f"ValueError: {e} for value: {raw_value}")
        continue  # エラー時はスキップ

    # タイムスタンプの範囲確認
    if start_timestamp <= timestamp < end_timestamp:
        if tx["to"].lower() == WALLET_ADDRESS.lower():
            total_in += value
        elif tx["from"].lower() == WALLET_ADDRESS.lower():
            total_out += value

# **IN - OUT の差額を計算**
net_amount = total_in - total_out

# Discord へ送信
message = f"""
📢 **{start_time.strftime('%Y-%m-%d %H:%M:%S')} ～ {now.strftime('%Y-%m-%d %H:%M:%S')} の SNPT 小計**
🟢 **IN:** {total_in:.4f} SNPT
🔴 **OUT:** {total_out:.4f} SNPT
📉 **NET (IN - OUT):** {net_amount:.4f} SNPT
"""

requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

print("✅ 6時間ごとの SNPT 小計を Discord に送信しました！")
