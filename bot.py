import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# --- Load variables from Railway environment ---
BOT_TOKEN = os.getenv("BOT_TOKEN")      # Set in Railway Environment Variables
CHAT_ID = int(os.getenv("CHAT_ID"))     # Your Telegram group chat ID, also in Railway

# Function to scrape Public Notices
def get_public_notices():
    url = "https://jeemain.nta.nic.in/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching the website: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Public Notice section
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

# Handler for /update command
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching Public Notices... ⏳")
    notices = get_public_notices()
    await update.message.reply_text(notices)

async def main():
    # Create bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add /update command
    app.add_handler(CommandHandler("update", update_command))

    print("Bot is ready. Waiting for /update commands...")
    
    # Start bot
    await app.start()
    await app.updater.start_polling()
    
    # Sleep forever (bot only wakes on commands)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
