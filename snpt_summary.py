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
