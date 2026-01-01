import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# --- Load Environment Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Safety checks
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing!")
if not CHAT_ID:
    raise ValueError("CHAT_ID is missing!")

try:
    CHAT_ID = int(CHAT_ID)
except ValueError:
    raise ValueError(f"CHAT_ID must be an integer. Got: {CHAT_ID}")

bot = Bot(token=BOT_TOKEN)

# --- Scrape Public Notices ---
def get_public_notices():
    url = "https://jeemain.nta.nic.in/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching the website: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    notices_section = soup.find("div", {"id": "publicNotice"})
    if not notices_section:
        return "No Public Notices found."

    notices = notices_section.find_all("a")
    if not notices:
        return "No Public Notices found."

    results = []
    for notice in notices:
        title = notice.get_text(strip=True)
        link = notice.get("href")
        if link and link.startswith("/"):
            link = "https://jeemain.nta.nic.in" + link
        results.append(f"{title}\n{link}")

    return "\n\n".join(results) if results else "No Public Notices found."

# --- Main Loop ---
def main():
    print("Bot is ready. Send /update in chat to get Public Notices.")
    while True:
        cmd = input("Type /update to test: ")
        if cmd.strip() == "/update":
            notices = get_public_notices()
            bot.send_message(chat_id=CHAT_ID, text=notices)

if __name__ == "__main__":
    main()
