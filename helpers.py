import re

from flask import redirect, url_for
from bijoy2unicode.converter import Unicode, conversionMap
from urllib.parse import urlparse, parse_qs

def redirect_dashboard(role):
    if role == "Admin":
        return redirect(url_for('admin_dashboard'))
    elif role == "Service Admin":
        return redirect(url_for('service_admin_dashboard'))
    elif role == "Teacher":
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))


def convert_bangla_text(text):
    converter = Unicode()

    if not text:
        return ""

    text = str(text).strip()

    try:
        converted = converter.convertBijoyToUnicode(text)

        return converted

    except Exception:
        return text


YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def youtube_embed_url(url):
    """Any common YouTube link -> embed URL, or None if no video ID can be found.

    Handles youtu.be/ID, youtube.com/watch?v=ID, /shorts/ID, /embed/ID, /live/ID,
    m.youtube.com and links with extra parameters (?si=..., &t=...).
    """
    url = str(url or "").strip()
    if not url:
        return None
    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("m."):
        host = host[2:]
    path_parts = [part for part in parsed.path.split("/") if part]

    video_id = None
    if host == "youtu.be" and path_parts:
        video_id = path_parts[0]
    elif host in ("youtube.com", "youtube-nocookie.com"):
        if path_parts[:1] == ["watch"]:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(path_parts) >= 2 and path_parts[0] in ("shorts", "embed", "live", "v"):
            video_id = path_parts[1]

    if not video_id or not YOUTUBE_ID.match(video_id):
        return None
    return f"https://www.youtube.com/embed/{video_id}"



