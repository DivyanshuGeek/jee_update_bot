import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# ------------------------------
# Load Telegram bot token & chat ID from Railway environment variables
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Safety checks
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing! Set it in Railway Environment Variables.")
if not CHAT_ID:
    raise ValueError("CHAT_ID is missing! Set it in Railway Environment Variables.")

try:
    CHAT_ID = int(CHAT_ID)
except ValueError:
    raise ValueError(f"CHAT_ID must be an integer. Got: {CHAT_ID}")

# ------------------------------
# Function to scrape Public Notices
# ------------------------------
def get_public_notices():
    url = "https://jeemain.nta.nic.in/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching the website: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Public Notice section (update selector if website changes)
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

# ------------------------------
# Handler for /update command
# ------------------------------
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching Public Notices... ⏳")
    notices = get_public_notices()
    await update.message.reply_text(notices)

# ------------------------------
# Main bot function
# ------------------------------
async def main():
    # Create bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add /update command handler
    app.add_handler(CommandHandler("update", update_command))

    print("Bot is ready. Sleeping until /update command...")

    # Start the bot
    await app.start()
    await app.updater.start_polling()

    # Sleep forever (bot only wakes on /update)
    await asyncio.Event().wait()

# ------------------------------
# Entry point
# ------------------------------
if __name__ == "__main__":
    asyncio.run(main())
