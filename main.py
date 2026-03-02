import os
import asyncio
import re
from telethon import TelegramClient, events

# ==============================
# VARIABLES DE ENTORNO (RAILWAY)
# ==============================
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

source_channel = "@chollosdeluxe"
target_channel = "@solochollos10"

# Si quieres preview del enlace (cajita con imagen/título), pon True.
# Ojo: Telethon por defecto no activa previews si no lo indicas. [page:0]
LINK_PREVIEW = True

client = TelegramClient("session_bot_chollos", api_id, api_hash)

# ==============================
# HELPERS
# ==============================
def is_amazon_url(url: str) -> bool:
    u = (url or "").lower()
    return (
        "amzn.to" in u
        or "amzn.eu" in u
        or "a.co" in u
        or "amazon." in u
    )

def clean_url(url: str) -> str:
    return (url or "").strip().rstrip(".,;:!?)])}\"'")

def extract_urls_from_text(text: str):
    # Evita comerse paréntesis/corchetes típicos de Markdown
    return re.findall(r'https?://[^\s\)\]\}]+', text or "")

def extract_urls_from_entities(message):
    urls = []
    ents = getattr(message, "entities", None) or []
    for ent in ents:
        # Links tipo: [texto](https://url) -> ent.url
        u = getattr(ent, "url", None)
        if u:
            urls.append(u)
    return urls

async def publish_amazon_links(amazon_links):
    seen = set()
    for link in amazon_links:
        link = clean_url(link)
        if not link or link in seen:
            continue
        seen.add(link)

        try:
            await client.send_message(target_channel, link, link_preview=LINK_PREVIEW)
            print(f"🔗 Publicado: {link}")
        except Exception as e:
            print(f"Error publicando {link}: {e}")

# ==============================
# HANDLER CANAL ORIGEN
# ==============================
async def process_source_message(event):
    msg = event.message
    text = event.raw_text or ""

    # 1) URLs visibles en el texto
    links = extract_urls_from_text(text)

    # 2) URLs “ocultas” en entidades (ej: markdown inline URL)
    links += extract_urls_from_entities(msg)

    # Filtra Amazon
    amazon_links = [l for l in links if is_amazon_url(l)]
    if not amazon_links:
        return

    await publish_amazon_links(amazon_links)

# ==============================
# MAIN
# ==============================
async def main():
    await client.start(bot_token=bot_token)
    print("🤖 BOT LINK-REPOST ACTIVADO ✅")
    print(f"✅ {source_channel} → {target_channel}")
    print(f"✅ Link preview: {LINK_PREVIEW}")  # Telethon permite controlar previews [page:0]

    @client.on(events.NewMessage(chats=source_channel))
    async def handler_source(event):
        await process_source_message(event)

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
