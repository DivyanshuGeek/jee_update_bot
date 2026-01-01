import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(BOT_TOKEN)

def get_public_notices():
    url = "https://jeemain.nta.nic.in/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    notices_section = soup.find("div", {"id": "publicNotice"})
    notices = notices_section.find_all("a") if notices_section else []
    return "\n\n".join(
        [f"{n.get_text(strip=True)}\n{'https://jeemain.nta.nic.in'+n.get('href') if n.get('href','').startswith('/') else n.get('href')}" for n in notices]
    ) or "No Public Notices found."

def update_command(update, context):
    notices = get_public_notices()
    context.bot.send_message(chat_id=CHAT_ID, text=notices)

updater = Updater(BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler("update", update_command))

updater.start_polling()
updater.idle()
