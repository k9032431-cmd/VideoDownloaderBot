"""yt-dlp bilen TikTok / Instagram / YouTube wideolaryny ýüklemek."""

import copy
import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yt_dlp

log = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://[^\s<>\"']+")
SUPPORTED_HOSTS = (
    "tiktok.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
)

# Telegram-yň wideo ölçeglerine görä synanyşylýan beýiklikler (iň gowudan başlap)
HEIGHTS = (1080, 720, 480, 360, 240)
MAX_ITEMS = 10  # Instagram karusel / sanaw üçin iň köp wideo

COOKIES_FILE = os.getenv("COOKIES_FILE", "/app/cookies.txt")


class DownloadError(Exception):
    """Ulanyja görkezilýän ýalňyşlyk."""


@dataclass
class Video:
    path: Path
    title: str
    duration: int | None
    width: int | None
    height: int | None


def find_url(text: str) -> str | None:
    for match in URL_RE.finditer(text or ""):
        url = match.group(0).rstrip(").,!?")
        host = re.sub(r"^https?://", "", url).split("/")[0].lower()
        if any(host == h or host.endswith("." + h) for h in SUPPORTED_HOSTS):
            return url
    return None


def _format(height: int) -> str:
    # TikTok-da "watermarked" bellikli formatlar (suw belgili) aýrylýar.
    nowm = "[format_note!*=?watermarked]"
    return (
        f"bv*[height<={height}]{nowm}+ba/"
        f"b[height<={height}]{nowm}/"
        f"b{nowm}/b"
    )


def _base_opts(outdir: Path) -> dict:
    opts = {
        "outtmpl": str(outdir / "%(id)s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
        "concurrent_fragment_downloads": 4,
        # Telegram-da hemme enjamda açylar ýaly H.264/AAC/mp4 ileri tutulýar
        "format_sort": ["vcodec:h264", "res", "acodec:aac", "ext:mp4:m4a"],
        "postprocessors": [
            {"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"},
        ],
        "postprocessor_args": {"videoremuxer": ["-movflags", "+faststart"]},
    }
    if os.path.isfile(COOKIES_FILE) and os.path.getsize(COOKIES_FILE) > 0:
        opts["cookiefile"] = COOKIES_FILE
    return opts


def _estimate_size(info: dict) -> int | None:
    parts = info.get("requested_formats") or [info]
    total = 0
    for f in parts:
        size = f.get("filesize") or f.get("filesize_approx")
        if not size:
            return None
        total += size
    return total


def _probe(path: Path) -> dict:
    """Faýlyň hakyky ölçeglerini ffprobe bilen almak."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout
        data = json.loads(out)
        stream = (data.get("streams") or [{}])[0]
        duration = float(data.get("format", {}).get("duration") or 0)
        return {"width": stream.get("width"), "height": stream.get("height"),
                "duration": int(duration) or None}
    except Exception:  # noqa: BLE001
        return {}


def _find_file(outdir: Path, info: dict) -> Path | None:
    for d in info.get("requested_downloads") or []:
        p = d.get("filepath")
        if p and os.path.isfile(p):
            return Path(p)
    files = [p for p in outdir.iterdir() if p.is_file() and p.suffix != ".part"]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def _download_entry(entry: dict, outdir: Path, max_bytes: int) -> Video:
    last_err = None
    for height in HEIGHTS:
        opts = _base_opts(outdir) | {"format": _format(height)}
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                planned = ydl.process_ie_result(copy.deepcopy(entry), download=False)
            except yt_dlp.utils.DownloadError as e:
                last_err = e
                continue
            est = _estimate_size(planned)
            if est and est > max_bytes * 1.05:
                log.info("%sp ~%d MB, has kiçisi synanyşylýar", height, est >> 20)
                continue
            for p in outdir.iterdir():
                p.unlink()
            info = ydl.process_ie_result(copy.deepcopy(entry), download=True)

        path = _find_file(outdir, info)
        if not path:
            raise DownloadError("Faýl tapylmady.")
        if path.stat().st_size <= max_bytes:
            meta = _probe(path)
            return Video(
                path=path,
                title=(info.get("title") or "")[:200],
                duration=meta.get("duration") or (int(info["duration"]) if info.get("duration") else None),
                width=meta.get("width") or info.get("width"),
                height=meta.get("height") or info.get("height"),
            )
        log.info("%sp faýl uly (%d MB), has kiçisi synanyşylýar", height, path.stat().st_size >> 20)

    if last_err:
        raise last_err
    limit_mb = max_bytes >> 20
    raise DownloadError(f"Wideo örän uly: Telegram {limit_mb} MB-dan uly faýly kabul etmeýär.")


def download(url: str, workdir: Path, max_bytes: int) -> list[Video]:
    """Sinhron: asyncio.to_thread içinde çagyryň."""
    with yt_dlp.YoutubeDL(_base_opts(workdir)) as ydl:
        info = ydl.extract_info(url, download=False, process=False)
        for _ in range(3):  # gysga salgylar (vt.tiktok.com we ş.m.) başga salga ugradýar
            if info.get("_type") not in ("url", "url_transparent"):
                break
            info = ydl.extract_info(info["url"], download=False, process=False)

    if info.get("_type") in ("playlist", "multi_video"):
        entries = [e for e in (info.get("entries") or []) if e][:MAX_ITEMS]
    else:
        entries = [info]
    if not entries:
        raise DownloadError("Bu salgyda wideo tapylmady.")

    videos = []
    for i, entry in enumerate(entries):
        if entry.get("_type") in ("url", "url_transparent"):
            with yt_dlp.YoutubeDL(_base_opts(workdir)) as ydl:
                entry = ydl.extract_info(entry["url"], download=False, process=False)
        sub = workdir / str(i)
        sub.mkdir(exist_ok=True)
        videos.append(_download_entry(entry, sub, max_bytes))
    return videos


def humanize_error(err: Exception) -> str:
    text = str(err).lower()
    if isinstance(err, DownloadError):
        return str(err)
    if "login" in text or "cookies" in text or "sign in" in text or "rate-limit" in text:
        return ("Bu wideony ýüklemek üçin sahypa giriş (cookies) talap edýär. "
                "Admin cookies.txt faýlyny goşmaly.")
    if "private" in text:
        return "Bu wideo ýapyk (private)."
    if "unavailable" in text or "not available" in text or "404" in text:
        return "Wideo tapylmady ýa-da pozuldy."
    if "no video" in text or "there is no video" in text:
        return "Bu postda wideo ýok."
    return "Wideony ýükläp bolmady. Salgyny barlaň ýa-da soňrak synanyşyň."
