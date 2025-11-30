import os
import re
from urllib.parse import parse_qs, urlparse

import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import TwitterPost, YouTubeVideo


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


def video_delete(request, video_id):
    """Delete a YouTube video from the list."""
    try:
        video = YouTubeVideo.objects.get(id=video_id)
        title = video.title
        video.delete()
        messages.success(request, f"Deleted: {title}")
    except YouTubeVideo.DoesNotExist:
        messages.error(request, "Video not found")
    return redirect("list")


def video_resync(request, video_id):
    """Resync YouTube video information from API."""
    try:
        video = YouTubeVideo.objects.get(id=video_id)

        # Fetch fresh title from YouTube
        title = get_video_title(video.video_id)
        if title:
            video.title = title
            video.save()
            messages.success(request, f"Resynced: {title}")
        else:
            messages.error(request, "Could not fetch updated video information")
    except YouTubeVideo.DoesNotExist:
        messages.error(request, "Video not found")
    return redirect("list")


def extract_tweet_id_and_handle(url):
    """Extract tweet ID and author handle from various X/Twitter URL formats."""
    # Remove whitespace
    url = url.strip()

    # Pattern for different X/Twitter URL formats
    # https://x.com/username/status/1234567890
    # https://twitter.com/username/status/1234567890
    patterns = [
        r"(?:x\.com|twitter\.com)/([a-zA-Z0-9_]+)/status/(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)  # handle, post_id

    return None, None


def get_tweet_info(post_id, author_handle):
    """Fetch tweet information from Twitter API v2."""
    try:
        # Get bearer token from environment
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        if not bearer_token:
            # No API credentials configured, return None
            return None

        # Check if SSL verification should be disabled (for development/proxy issues)
        verify_ssl = os.getenv("TWITTER_VERIFY_SSL", "true").lower() != "false"

        # Suppress SSL warnings if verification is disabled
        if not verify_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            print("Warning: SSL verification disabled for Twitter API")

        # Use requests directly with proper SSL configuration
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "MindTreeLog/1.0",
        }

        url = (
            f"https://api.twitter.com/2/tweets/{post_id}"
            f"?tweet.fields=text,author_id"
            f"&expansions=author_id"
            f"&user.fields=name,username"
        )

        # Make request with SSL verification control
        response = requests.get(url, headers=headers, verify=verify_ssl, timeout=10)

        # Debug logging
        print(f"Twitter API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Twitter API Response: {data}")

            # Extract tweet data
            if "data" in data:
                tweet = data["data"]
                text = tweet.get("text", "")

                # Truncate if too long
                if len(text) > 500:
                    text = text[:497] + "..."

                # Extract author info from includes
                author_name = author_handle
                if "includes" in data and "users" in data["includes"]:
                    users = data["includes"]["users"]
                    if users:
                        author_name = users[0].get("name", author_handle)

                print(f"✅ Successfully fetched tweet: {text[:50]}...")
                return {"author_name": author_name, "text": text}
            print(f"⚠️ No 'data' field in response: {data}")

        elif response.status_code == 401:
            print("❌ Twitter API authentication error: Check your bearer token")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except Exception:
                pass
        elif response.status_code == 429:
            print("⚠️ Twitter API rate limit exceeded (Free tier: 1,500 tweets/month)")
            print("💡 Tip: Posts are still saved with placeholder text. Edit in admin or wait for limit reset.")
        elif response.status_code == 403:
            print("❌ Twitter API Forbidden (403): Your app may not have the required permissions")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except Exception:
                pass
        else:
            print(f"❌ Twitter API error: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except Exception:
                print(f"Response text: {response.text[:200]}")

    except requests.exceptions.SSLError as e:
        print(f"SSL Error: {e}")
        print("Try setting TWITTER_VERIFY_SSL=false in .env file (development only)")
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching tweet info: {e}")
    except Exception as e:
        print(f"Error fetching tweet info: {e}")

    return None


def twitter_list(request):
    if request.method == "POST":
        post_url = request.POST.get("post_url", "").strip()

        if not post_url:
            messages.error(request, "Please enter an X/Twitter URL")
            return redirect("xlist")

        # Extract post ID and handle
        author_handle, post_id = extract_tweet_id_and_handle(post_url)
        if not post_id or not author_handle:
            messages.error(request, "Invalid X/Twitter URL")
            return redirect("xlist")

        # Check if post already exists
        if TwitterPost.objects.filter(post_id=post_id).exists():
            messages.warning(request, "This post is already in your list")
            return redirect("xlist")

        # Fetch post info (optional - fallback to defaults if API fails)
        post_info = get_tweet_info(post_id, author_handle)

        if post_info:
            author_name = post_info["author_name"]
            text = post_info["text"]
        else:
            # Use defaults if we can't fetch from API
            author_name = author_handle
            text = f"Post from @{author_handle}"
            messages.warning(
                request,
                f"Added post from @{author_handle} (Could not fetch full details from X/Twitter API)",
            )

        # Save post
        TwitterPost.objects.create(
            post_id=post_id,
            author_handle=author_handle,
            author_name=author_name,
            text=text,
        )

        if post_info:
            messages.success(request, f"Added post from @{author_handle}")
        return redirect("xlist")

    posts = TwitterPost.objects.all().order_by("-id")
    return render(request, "youtube/twitter_list.html", {"posts": posts})


def twitter_delete(request, post_id):
    """Delete a Twitter post from the list."""
    try:
        post = TwitterPost.objects.get(id=post_id)
        author = post.author_handle
        post.delete()
        messages.success(request, f"Deleted post from @{author}")
    except TwitterPost.DoesNotExist:
        messages.error(request, "Post not found")
    return redirect("xlist")


def twitter_resync(request, post_id):
    """Resync Twitter post information from API."""
    try:
        post = TwitterPost.objects.get(id=post_id)

        # Fetch fresh data from Twitter
        post_info = get_tweet_info(post.post_id, post.author_handle)
        if post_info:
            post.author_name = post_info["author_name"]
            post.text = post_info["text"]
            post.save()
            messages.success(request, f"Resynced post from @{post.author_handle}")
        else:
            messages.warning(
                request,
                f"Could not resync post from @{post.author_handle}. "
                "Check logs for details (API rate limit, SSL issues, etc.)",
            )
    except TwitterPost.DoesNotExist:
        messages.error(request, "Post not found")
    return redirect("xlist")
