import os
import time
import requests

# ─── ENV VARIABLES ─────────────────────────────
ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
GROUP_ID = os.getenv("GROUP_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

headers = {
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
    "User-Agent": "Mozilla/5.0"
}

url = f"https://economy.roblox.com/v2/groups/{GROUP_ID}/transactions?transactionType=Sale&limit=10"

seen_ids = []
print("🚀 Bot started...")

def send_discord_message(content):
    try:
        data = {"content": content}
        response = requests.post(DISCORD_WEBHOOK, json=data)
        if response.status_code == 204:
            print("✅ Discord message sent")
        else:
            print(f"❌ Failed to send message, status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Discord error: {e}")

# ─── MAIN LOOP ────────────────────────────────
while True:
    try:
        r = requests.get(url, headers=headers)
        print("Status:", r.status_code)

        if r.status_code == 200:
            data = r.json()["data"]

            for tx in data:
                tx_id = tx["id"]

                if tx_id not in seen_ids:
                    seen_ids.append(tx_id)

                    username = tx["agent"]["name"]
                    item = tx["details"]["name"]
                    amount = tx["currency"]["amount"]

                    print(f"🆕 NEW SALE: {username} | {item} | {amount}")

                    # Send to Discord
                    content = f"🛒 **NEW SALE**\nUser: {username}\nItem: {item}\nAmount: {amount}"
                    send_discord_message(content)
        else:
            print("Error:", r.text)

    except Exception as e:
        print("Crash:", e)

    time.sleep(60)
