import os
import re
import asyncio
import random
from telethon import TelegramClient, events
from dotenv import load_dotenv
from database import init_db, link_exists, save_link

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE_NUMBER")

source_channels = [
    "chollosdeluxe",
    "cholloschina"
]

destination_channel = "solochollos10"

AMAZON_REGEX = r"(https?://[^\s]*amazon\.[^\s]+|https?://amzn\.to/[^\s]+)"

client = TelegramClient("session", api_id, api_hash)


def clean_link(link: str) -> str:
    # Elimina parámetros de tracking básicos
    return link.split("?")[0]


@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    message_text = event.message.text

    if not message_text:
        return

    matches = re.findall(AMAZON_REGEX, message_text)

    if not matches:
        return

    for link in matches:
        cleaned = clean_link(link)

        if link_exists(cleaned):
            print("Duplicado detectado")
            return

        save_link(cleaned)

        formatted = f"🔥 CHOLLO AMAZON 🔥\n\n{message_text}"

        await asyncio.sleep(random.uniform(2, 5))  # Anti-flood delay

        try:
            await client.send_message(destination_channel, formatted)
            print("Mensaje enviado")
        except Exception as e:
            print("Error enviando:", e)


async def main():
    init_db()
    await client.start(phone=phone)
    print("Bot PRO activo...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
