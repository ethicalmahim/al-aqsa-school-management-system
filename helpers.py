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


def youtube_embed_url(url):
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/")
    else:
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    return f"https://www.youtube.com/embed/{video_id}"



