import os
import time
import requests
import smtplib
from email.message import EmailMessage

# ===== ENV VARS =====
ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
GROUP_ID = os.getenv("GROUP_ID")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

if not all([ROBLOX_COOKIE, GROUP_ID, EMAIL_ADDRESS, EMAIL_PASSWORD, TO_EMAIL]):
    print("❌ Missing one or more environment variables!")
    exit(1)

# ===== HEADERS & URL =====
headers = {
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
    "User-Agent": "Mozilla/5.0"
}

url = f"https://economy.roblox.com/v2/groups/{GROUP_ID}/transactions?transactionType=Sale&limit=10"

seen_ids = set()

print("🚀 Bot started...")

# ===== EMAIL FUNCTION =====
def send_email(username, item, amount):
    msg = EmailMessage()
    msg["Subject"] = "🛒 New Roblox Group Sale!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    msg.set_content(
        f"""
New sale detected!

Buyer: {username}
Item: {item}
Amount: {amount} Robux

– Roblox Sales Bot
"""
    )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("📧 Email sent to", TO_EMAIL)
    except Exception as e:
        print("❌ Email failed:", e)

# ===== MAIN LOOP =====
while True:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print("Status:", r.status_code)

        if r.status_code == 200:
            data = r.json()["data"]

            print("🔢 Transactions received:", len(data))
            print("👀 Seen IDs:", len(seen_ids))

            for tx in data:
                tx_id = tx["id"]
                print("➡️ Checking:", tx_id)

                if tx_id not in seen_ids:
                    username = tx["agent"]["name"]
                    item = tx["details"]["name"]
                    amount = tx["currency"]["amount"]

                    print("🆕 NEW SALE:", username, item, amount)

                    # send email FIRST
                    send_email(username, item, amount)

                    # mark as seen AFTER success
                    seen_ids.add(tx_id)
                else:
                    print("⏭️ Already seen:", tx_id)

        else:
            print("❌ API Error:", r.text)

    except Exception as e:
        print("💥 Crash:", e)

    print("⏳ Sleeping 60s...\n")
    time.sleep(60)