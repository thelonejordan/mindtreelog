import os
import re
from urllib.parse import parse_qs, urlparse

import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import TwitterPost, YouTubeVideo


def home(request):
    return redirect("collections_list", collection_type="youtube")


def collections_list(request, collection_type="youtube"):
    """Unified view for both YouTube videos and Twitter posts."""
    # Validate collection type
    if collection_type not in ["youtube", "twitter"]:
        return redirect("collections_list", collection_type="youtube")

    if request.method == "POST":
        if collection_type == "youtube":
            return handle_youtube_add(request)
        return handle_twitter_add(request)

    # Get items based on type
    if collection_type == "youtube":
        items = YouTubeVideo.objects.all().order_by("-id")
    else:
        items = TwitterPost.objects.all().order_by("-id")

    context = {
        "collection_type": collection_type,
        "items": items,
    }
    return render(request, "collectibles/collections_list.html", context)


def handle_youtube_add(request):
    """Handle adding a YouTube video."""
    video_url = request.POST.get("item_url", "").strip()

    if not video_url:
        messages.error(request, "Please enter a YouTube URL")
        return redirect("collections_list", collection_type="youtube")

    # Extract video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        messages.error(request, "Invalid YouTube URL")
        return redirect("collections_list", collection_type="youtube")

    # Check if video already exists
    if YouTubeVideo.objects.filter(video_id=video_id).exists():
        messages.warning(request, "This video is already in your list")
        return redirect("collections_list", collection_type="youtube")

    # Fetch video title
    title = get_video_title(video_id)
    if not title:
        messages.error(request, "Could not fetch video information")
        return redirect("collections_list", collection_type="youtube")

    # Save video
    YouTubeVideo.objects.create(video_id=video_id, title=title)
    messages.success(request, f"Added: {title}")
    return redirect("collections_list", collection_type="youtube")


def handle_twitter_add(request):
    """Handle adding a Twitter post."""
    post_url = request.POST.get("item_url", "").strip()

    if not post_url:
        messages.error(request, "Please enter a Twitter/X URL")
        return redirect("collections_list", collection_type="twitter")

    # Extract tweet ID and handle
    result = extract_tweet_id_and_handle(post_url)
    if not result:
        messages.error(request, "Invalid Twitter/X URL")
        return redirect("collections_list", collection_type="twitter")

    post_id, author_handle = result

    # Check if post already exists
    if TwitterPost.objects.filter(post_id=post_id).exists():
        messages.warning(request, "This post is already in your list")
        return redirect("collections_list", collection_type="twitter")

    # Fetch tweet info
    tweet_info = get_tweet_info(post_id, author_handle)

    # Create post (with or without fetched info)
    if tweet_info:
        TwitterPost.objects.create(
            post_id=post_id,
            author_handle=author_handle,
            text=tweet_info["text"],
            author_name=tweet_info["author_name"],
        )
        messages.success(request, f"Added post from @{author_handle}")
    else:
        # Save with placeholder text
        TwitterPost.objects.create(
            post_id=post_id,
            author_handle=author_handle,
            text=f"Post {post_id[:10]}...",
            author_name=author_handle,
        )
        messages.warning(
            request,
            f"Added post from @{author_handle} (info fetch failed - post saved with placeholder)",
        )

    return redirect("collections_list", collection_type="twitter")


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
        print(f"Fetching video title from: {url}")
        response = requests.get(url, timeout=5)
        print(f"YouTube API Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            title = data.get("title")
            print(f"✓ Successfully fetched video: {title}")
            return title
        print(f"YouTube API error: Status {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching video title: {e}")
    except Exception as e:
        print(f"Unexpected error in get_video_title: {e}")
    return None


def video_list(request):
    """Legacy redirect to unified collections view."""
    return redirect("collections_list", collection_type="youtube")


def video_delete(request, video_id):
    """Delete a YouTube video from the list."""
    try:
        video = YouTubeVideo.objects.get(id=video_id)
        title = video.title
        video.delete()
        messages.success(request, f"Deleted: {title}")
    except YouTubeVideo.DoesNotExist:
        messages.error(request, "Video not found")
    return redirect("collections_list", collection_type="youtube")


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
    return redirect("collections_list", collection_type="youtube")


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
    """Legacy redirect to unified collections view."""
    return redirect("collections_list", collection_type="twitter")


def twitter_delete(request, post_id):
    """Delete a Twitter post from the list."""
    try:
        post = TwitterPost.objects.get(id=post_id)
        author = post.author_handle
        post.delete()
        messages.success(request, f"Deleted post from @{author}")
    except TwitterPost.DoesNotExist:
        messages.error(request, "Post not found")
    return redirect("collections_list", collection_type="twitter")


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
    return redirect("collections_list", collection_type="twitter")
