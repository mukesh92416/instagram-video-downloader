from django.shortcuts import render
from django.http import FileResponse, Http404
from django.conf import settings
import os, glob

from .downloader import get_instagram_preview, download_instagram


def index(request):
    context = {}

    if request.method == "POST":
        url = request.POST.get("url", "").strip()
        context["url"] = url

        if "instagram.com" not in url:
            context["error"] = "❌ Invalid Instagram URL"

        elif "preview" in request.POST:
            preview = get_instagram_preview(url)
            if preview:
                context["preview"] = preview
            else:
                context["error"] = "❌ Preview not available"

    return render(request, "downloader/index.html", context)


import shutil
from django.http import FileResponse, HttpResponse, Http404

def download_file(request):
    url = request.GET.get("url")
    if not url:
        raise Http404("No URL provided")

    download_dir = settings.MEDIA_ROOT

    # 🔑 CLEAR OLD FILES (IMPORTANT)
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir)

    # Try downloading
    try:
        download_instagram(url)
    except Exception as e:
        print("Download error:", e)

    files = glob.glob(os.path.join(download_dir, "*"))

    # ❌ If nothing downloaded → honest response
    if not files:
        return HttpResponse(
            "This Instagram post could not be downloaded (photo-only or restricted).",
            status=200
        )

    # ✅ Send newly downloaded file
    latest_file = max(files, key=os.path.getctime)

    return FileResponse(
        open(latest_file, "rb"),
        as_attachment=True,
        filename=os.path.basename(latest_file)
    )
