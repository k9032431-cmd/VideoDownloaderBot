"""Telegram bot: TikTok / Instagram / YouTube wideolaryny suw belgisiz ugradýar."""

import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, InputMediaVideo, Message
from aiogram.utils.chat_action import ChatActionSender

from . import downloader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "").strip()
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3") or 3)
ALLOWED_USERS = {
    int(x) for x in os.getenv("ALLOWED_USERS", "").replace(" ", "").split(",") if x
}
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/downloads"))

# Adaty Bot API 50 MB; ýerli Bot API serweri 2 GB.
MAX_BYTES = (2000 if LOCAL_API_URL else 49) * 1024 * 1024

semaphore = asyncio.Semaphore(MAX_CONCURRENT)
busy_users: set[int] = set()
dp = Dispatcher()

START_TEXT = (
    "👋 Salam! Maňa <b>TikTok</b>, <b>Instagram</b> ýa-da <b>YouTube</b> "
    "wideosynyň salgysyny (ssylkasyny) ugradyň — men ony suw belgisiz "
    "(водяной знак-syz) size ugradaryn."
)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(START_TEXT)


@dp.message(F.text | F.caption)
async def handle_link(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id if message.from_user else 0
    url = downloader.find_url(message.text or message.caption or "")
    if not url:
        if message.chat.type == "private":
            await message.answer("Diňe TikTok, Instagram ýa-da YouTube salgysyny ugradyň.")
        return
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await message.answer("⛔ Bu boty ulanmaga rugsadyňyz ýok.")
        return
    if user_id in busy_users:
        await message.reply("⏳ Öňki wideoňyz entek ýüklenýär, garaşyň.")
        return

    busy_users.add(user_id)
    status = await message.reply("⏳ Ýüklenýär...")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="dl_", dir=DOWNLOAD_DIR))
    workdir.chmod(0o755)  # ýerli Bot API serweri faýly okap bilmeli
    try:
        async with semaphore:
            async with ChatActionSender(bot=bot, chat_id=message.chat.id,
                                        action=ChatAction.UPLOAD_VIDEO):
                videos = await asyncio.to_thread(
                    downloader.download, url, workdir, MAX_BYTES
                )
                await send_videos(message, videos)
        await status.delete()
    except Exception as e:  # noqa: BLE001 - ulanyja düşnükli jogap bermeli
        log.warning("Ýalňyşlyk %s: %r", url, e)
        await status.edit_text("❌ " + downloader.humanize_error(e))
    finally:
        busy_users.discard(user_id)
        shutil.rmtree(workdir, ignore_errors=True)


async def send_videos(message: Message, videos: list[downloader.Video]) -> None:
    def media(v: downloader.Video) -> dict:
        return dict(
            duration=v.duration,
            width=v.width,
            height=v.height,
            supports_streaming=True,
        )

    if len(videos) == 1:
        v = videos[0]
        await message.reply_video(FSInputFile(v.path), **media(v))
        return
    group = [InputMediaVideo(media=FSInputFile(v.path), **media(v)) for v in videos]
    await message.reply_media_group(group)


async def logout_from_cloud_once() -> None:
    """Ýerli serwere geçmezden öň bot bir gezek bulut Bot API-den çykmaly."""
    marker = DOWNLOAD_DIR / ".logged_out_from_cloud"
    if marker.exists():
        return
    try:
        async with Bot(BOT_TOKEN) as cloud_bot:
            await cloud_bot.log_out()
        log.info("Bulut Bot API-den çykyldy (bir gezeklik).")
    except Exception as e:  # noqa: BLE001 - eýýäm çykylan bolup biler
        log.info("log_out: %s", e)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    marker.touch()


async def main() -> None:
    # Uly faýllary ugratmak üçin wagt çägi uly goýulýar
    session = AiohttpSession(timeout=900)
    if LOCAL_API_URL:
        await logout_from_cloud_once()
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(LOCAL_API_URL, is_local=True),
            timeout=900,
        )
        log.info("Ýerli Bot API serweri ulanylýar: %s (2 GB çäk)", LOCAL_API_URL)
    bot = Bot(BOT_TOKEN, session=session,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    log.info("Bot işledi: @%s", me.username)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
