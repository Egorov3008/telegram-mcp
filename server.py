import asyncio
import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel, DocumentAttributeAudio, DocumentAttributeVideo

from config import TG_API_ID, TG_API_HASH, SESSION_PATH, DOWNLOADS_PATH

# Log only to stderr to avoid interfering with stdio transport
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

client: TelegramClient | None = None


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[None]:
    global client
    client = TelegramClient(SESSION_PATH, TG_API_ID, TG_API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("Сессия не авторизована. Сначала запустите auth.py", file=sys.stderr)
        sys.exit(1)
    try:
        yield
    finally:
        await client.disconnect()


mcp = FastMCP("telegram", lifespan=lifespan)


def _resolve_chat_id(chat_id: str):
    """Convert string chat_id to int if numeric, otherwise return as-is for @username."""
    try:
        return int(chat_id)
    except ValueError:
        return chat_id


def _get_media_duration(document) -> int | None:
    """Extract duration from a Document's attributes."""
    if document and hasattr(document, "attributes"):
        for attr in document.attributes:
            if isinstance(attr, (DocumentAttributeAudio, DocumentAttributeVideo)):
                return attr.duration
    return None


def _entity_type(entity) -> str:
    if isinstance(entity, User):
        return "user"
    if isinstance(entity, Channel):
        return "channel" if entity.broadcast else "group"
    if isinstance(entity, Chat):
        return "group"
    return "unknown"


@mcp.tool()
async def get_chats(limit: int = 50) -> str:
    """Get list of Telegram dialogs (chats). Returns name, id, type, and unread count."""
    dialogs = await client.get_dialogs(limit=limit)
    lines = []
    for d in dialogs:
        entity_type = _entity_type(d.entity)
        lines.append(
            f"- {d.name} | id: {d.entity.id} | type: {entity_type} | unread: {d.unread_count}"
        )
    return "\n".join(lines) if lines else "No dialogs found."


@mcp.tool()
async def get_messages(chat_id: str, limit: int = 20) -> str:
    """Get recent messages from a chat. chat_id can be numeric ID or @username."""
    entity = await client.get_entity(_resolve_chat_id(chat_id))
    messages = await client.get_messages(entity, limit=limit)
    lines = []
    for msg in reversed(messages):
        sender_name = "Unknown"
        if msg.sender:
            if isinstance(msg.sender, User):
                sender_name = msg.sender.first_name or ""
                if msg.sender.last_name:
                    sender_name += f" {msg.sender.last_name}"
            else:
                sender_name = getattr(msg.sender, "title", "Unknown")
        date_str = msg.date.strftime("%Y-%m-%d %H:%M")
        if msg.text:
            text = msg.text
        elif msg.voice:
            dur = _get_media_duration(msg.voice)
            text = f"[voice message, {dur}s]" if dur else "[voice message]"
        elif msg.video_note:
            dur = _get_media_duration(msg.video_note)
            text = f"[video message, {dur}s]" if dur else "[video message]"
        elif msg.audio:
            dur = _get_media_duration(msg.audio)
            text = f"[audio, {dur}s]" if dur else "[audio]"
        else:
            text = "[media/service message]"
        lines.append(f"[{date_str}] (id:{msg.id}) {sender_name}: {text}")
    return "\n".join(lines) if lines else "No messages found."


@mcp.tool()
async def send_message(chat_id: str, text: str) -> str:
    """Send a message to a chat. chat_id can be numeric ID or @username."""
    entity = await client.get_entity(_resolve_chat_id(chat_id))
    msg = await client.send_message(entity, text)
    return f"Message sent (id: {msg.id})"


@mcp.tool()
async def count_user_messages(chat_id: str, user_id: int) -> str:
    """Count messages from a specific user in a chat for today (UTC)."""
    entity = await client.get_entity(_resolve_chat_id(chat_id))
    user = await client.get_entity(user_id)

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = 0
    async for msg in client.iter_messages(entity, from_user=user, offset_date=None):
        if msg.date < today_start:
            break
        count += 1

    user_name = user.first_name or str(user_id)
    return f"{user_name} sent {count} messages today in this chat."


@mcp.tool()
async def download_voice_message(chat_id: str, message_id: int) -> str:
    """Download a voice/video/audio message by its ID. Returns the absolute path to the downloaded file."""
    entity = await client.get_entity(_resolve_chat_id(chat_id))
    msg = await client.get_messages(entity, ids=message_id)
    if not msg:
        return f"Message {message_id} not found."
    if not msg.media:
        return f"Message {message_id} has no media."
    path = await client.download_media(msg, file=str(DOWNLOADS_PATH) + "/")
    if not path:
        return "Failed to download media."
    return f"Downloaded: {path}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
