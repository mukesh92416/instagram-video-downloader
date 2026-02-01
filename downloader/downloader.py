import yt_dlp
import os
import requests
from bs4 import BeautifulSoup
from django.conf import settings

# ---------- PREVIEW (NO yt-dlp) ----------
def get_instagram_preview(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    og_image = soup.find("meta", property="og:image")
    og_title = soup.find("meta", property="og:title")

    if not og_image:
        return None

    return {
        "thumbnail": og_image["content"],
        "title": og_title["content"] if og_title else "Instagram Post"
    }


# ---------- DOWNLOAD (yt-dlp) ----------
def download_instagram(url):
    download_path = settings.MEDIA_ROOT

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        # ✅ save videos + photos
        'outtmpl': os.path.join(
            download_path,
            '%(uploader)s_%(id)s_%(playlist_index)s.%(ext)s'
        ),

        # ✅ allow carousels / photos
        'noplaylist': False,
        'yes_playlist': True,

        # ✅ VERY IMPORTANT: do NOT crash on "no video"
        'ignoreerrors': True,

        # ✅ do not force video-only formats
        'format': 'best',

        'merge_output_format': 'mp4',
        'restrictfilenames': True,
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        # 🔒 Do NOT crash Django for photo posts
        print("Download warning:", e)
