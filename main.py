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

seen_ids = set()
first_run = True
print("🚀 Bot started...")

# ─── FUNCTION TO SEND DISCORD MESSAGE ─────────
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
            data = r.json().get("data", [])
            print(f"🔢 Transactions received: {len(data)}")
            tx_ids_in_batch = [str(tx["id"]) for tx in data]

            # Sort oldest first
            data.sort(key=lambda tx: int(tx["id"]))

            # ─── FIRST RUN ──────────────────────────
            if first_run:
                print(f"⚡ First run: sending all {len(data)} transactions")
                for tx in data:
                    username = tx["agent"]["name"]
                    item = tx["details"]["name"]
                    amount = tx["currency"]["amount"]

                    content = f"🛒 **SALE**\nUser: {username}\nItem: {item}\nAmount: {amount}"
                    send_discord_message(content)

                    seen_ids.add(str(tx["id"]))
                first_run = False
            else:
                # ─── NORMAL LOOP ───────────────────
                new_sales_count = 0
                for tx in data:
                    tx_id = str(tx["id"])
                    if tx_id not in seen_ids:
                        seen_ids.add(tx_id)
                        new_sales_count += 1

                        username = tx["agent"]["name"]
                        item = tx["details"]["name"]
                        amount = tx["currency"]["amount"]

                        print(f"🆕 NEW SALE: {username} | {item} | {amount}")

                        content = f"🛒 **NEW SALE**\nUser: {username}\nItem: {item}\nAmount: {amount}"
                        send_discord_message(content)

                if new_sales_count == 0:
                    print("⏳ No new sales this round")
                else:
                    print(f"⚡ Sent {new_sales_count} new sale(s)")

        else:
            print("❌ Error:", r.text)

    except Exception as e:
        print("💥 Crash:", e)

    time.sleep(60)