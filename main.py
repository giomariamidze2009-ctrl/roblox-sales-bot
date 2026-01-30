import os
import time
import requests

# ─── ENV VARIABLES ─────────────────────────────
ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
GROUP_ID = os.getenv("GROUP_ID")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

if not all([ROBLOX_COOKIE, GROUP_ID, DISCORD_WEBHOOK]):
    raise Exception("Missing ENV variables: ROBLOX_COOKIE, GROUP_ID, DISCORD_WEBHOOK")

headers = {
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
    "User-Agent": "Mozilla/5.0"
}

# Increase limit for safety
url = f"https://economy.roblox.com/v2/groups/{GROUP_ID}/transactions?transactionType=Sale&limit=50"

print("🚀 Roblox Sale Bot Started...")

last_seen_id = None   # Only track latest sale ID

# ─── FUNCTION TO SEND DISCORD MESSAGE ─────────
def send_discord_message(content):
    try:
        data = {"content": content}
        r = requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
        if r.status_code == 204:
            print("✅ Discord sent")
        else:
            print(f"❌ Discord failed: {r.status_code} | {r.text}")
    except Exception as e:
        print(f"❌ Discord error: {e}")

# ─── MAIN LOOP ────────────────────────────────
while True:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print("Status:", r.status_code)

        if r.status_code != 200:
            print("❌ Roblox API error:", r.text)
            time.sleep(30)
            continue

        data = r.json().get("data", [])

        if not data:
            print("⚠️ No transactions returned")
            time.sleep(60)
            continue

        # Sort newest → oldest
        data.sort(key=lambda tx: int(tx["id"]), reverse=True)

        # First run → just initialize pointer
        if last_seen_id is None:
            last_seen_id = str(data[0]["id"])
            print("⚡ Initialized. Waiting for new sales...")
        else:
            new_sales = []

            for tx in data:
                tx_id = str(tx["id"])
                if tx_id == last_seen_id:
                    break
                new_sales.append(tx)

            if new_sales:
                # Send oldest first
                for tx in reversed(new_sales):
                    username = tx["agent"]["name"]
                    item = tx["details"]["name"]
                    amount = tx["currency"]["amount"]

                    print(f"🆕 NEW SALE: {username} | {item} | {amount}")

                    msg = (
                        f"🛒 **NEW SALE**\n"
                        f"👤 User: {username}\n"
                        f"📦 Item: {item}\n"
                        f"💰 Amount: {amount}"
                    )

                    send_discord_message(msg)

                # Update pointer to newest transaction
                last_seen_id = str(data[0]["id"])
                print(f"⚡ Sent {len(new_sales)} new sale(s)")
            else:
                print("⏳ No new sales")

    except Exception as e:
        print("💥 Crash:", e)

    time.sleep(60)
