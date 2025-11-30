import re
from urllib.parse import parse_qs, urlparse

import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import YouTubeVideo


def home(request):
    return HttpResponse("Hello, Django!")


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    # Remove whitespace
    url = url.strip()

    # Pattern for different YouTube URL formats
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If no pattern matches, check if it's just the video ID
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    return None


def get_video_title(video_id):
    """Fetch video title from YouTube using oEmbed API."""
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("title")
    except Exception:
        pass
    return None


def video_list(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url", "").strip()

        if not video_url:
            messages.error(request, "Please enter a YouTube URL")
            return redirect("list")

        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            messages.error(request, "Invalid YouTube URL")
            return redirect("list")

        # Check if video already exists
        if YouTubeVideo.objects.filter(video_id=video_id).exists():
            messages.warning(request, "This video is already in your list")
            return redirect("list")

        # Fetch video title
        title = get_video_title(video_id)
        if not title:
            messages.error(request, "Could not fetch video information")
            return redirect("list")

        # Save video
        YouTubeVideo.objects.create(video_id=video_id, title=title)
        messages.success(request, f"Added: {title}")
        return redirect("list")

    videos = YouTubeVideo.objects.all().order_by("-id")
    return render(request, "youtube/video_list.html", {"videos": videos})
