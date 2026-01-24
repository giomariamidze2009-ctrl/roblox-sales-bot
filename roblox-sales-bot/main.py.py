import os
import time
import requests

ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
GROUP_ID = os.getenv("GROUP_ID")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

headers = {
    "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}",
    "User-Agent": "Mozilla/5.0"
}

url = f"https://economy.roblox.com/v2/groups/{GROUP_ID}/transactions?transactionType=Sale&limit=10"

seen_ids = set()

print("Bot started...")

while True:
    try:
        r = requests.get(url, headers=headers)
        print("Status:", r.status_code)

        if r.status_code == 200:
            data = r.json()["data"]

            for tx in data:
                tx_id = tx["id"]

                if tx_id not in seen_ids:
                    seen_ids.add(tx_id)

                    username = tx["agent"]["name"]
                    item = tx["details"]["name"]
                    amount = tx["currency"]["amount"]

                    print("NEW SALE:", username, item, amount)

                    # (email sending goes here later)

        else:
            print("Error:", r.text)

    except Exception as e:
        print("Crash:", e)

    time.sleep(60)