import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
from django.contrib import messages
from django.shortcuts import redirect, render

COLLECTION_TYPES = ("youtube", "twitter", "arxiv", "github")
COLLECTION_METADATA = {
    "youtube": {
        "label": "YouTube Videos",
        "option_label": "📹 YouTube Videos",
        "item_label": "video",
        "empty_icon": "📹",
        "empty_text": "No videos yet",
        "input_label": "YouTube URL",
        "input_placeholder": "https://www.youtube.com/watch?v=...",
        "add_title": "Add YouTube Video",
    },
    "twitter": {
        "label": "X/Twitter Posts",
        "option_label": "X / Twitter Posts",
        "item_label": "post",
        "empty_icon": "X",
        "empty_text": "No posts yet",
        "input_label": "Twitter/X URL",
        "input_placeholder": "https://x.com/username/status/...",
        "add_title": "Add X/Twitter Post",
    },
    "arxiv": {
        "label": "arXiv Papers",
        "option_label": "📄 arXiv Papers",
        "item_label": "paper",
        "empty_icon": "📄",
        "empty_text": "No papers yet",
        "input_label": "arXiv link or ID",
        "input_placeholder": "https://arxiv.org/abs/2403.12345",
        "add_title": "Add arXiv Paper",
    },
    "github": {
        "label": "GitHub Repos",
        "option_label": "🐙 GitHub Repos",
        "item_label": "repository",
        "empty_icon": "🐙",
        "empty_text": "No repositories yet",
        "input_label": "GitHub repo link or owner/repo",
        "input_placeholder": "https://github.com/owner/repo",
        "add_title": "Add GitHub Repo",
    },
}

COLLECTION_OPTIONS = [{"value": key, "label": meta["option_label"]} for key, meta in COLLECTION_METADATA.items()]

from .models import ArxivPaper, GithubRepo, TwitterPost, YouTubeVideo


def home(request):
    return redirect("collections_list", collection_type="youtube")


def collections_list(request, collection_type="youtube"):
    """Unified view for all collection types."""
    if collection_type not in COLLECTION_TYPES:
        return redirect("collections_list", collection_type="youtube")

    handler_map = {
        "youtube": handle_youtube_add,
        "twitter": handle_twitter_add,
        "arxiv": handle_arxiv_add,
        "github": handle_github_add,
    }

    if request.method == "POST":
        handler = handler_map.get(collection_type)
        if handler:
            return handler(request)

    query_map = {
        "youtube": YouTubeVideo.objects.order_by("-id"),
        "twitter": TwitterPost.objects.order_by("-id"),
        "arxiv": ArxivPaper.objects.order_by("-id"),
        "github": GithubRepo.objects.order_by("-id"),
    }

    items = query_map.get(collection_type, YouTubeVideo.objects.none())

    context = {
        "collection_type": collection_type,
        "items": items,
        "collection_types": COLLECTION_TYPES,
        "collection_metadata": COLLECTION_METADATA,
        "collection_options": COLLECTION_OPTIONS,
        "current_meta": COLLECTION_METADATA[collection_type],
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

    author_handle, post_id = result

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


def handle_arxiv_add(request):
    """Handle adding an arXiv paper."""
    paper_url = request.POST.get("item_url", "").strip()

    if not paper_url:
        messages.error(request, "Please enter an arXiv link or ID")
        return redirect("collections_list", collection_type="arxiv")

    arxiv_id = extract_arxiv_id(paper_url)
    if not arxiv_id:
        messages.error(request, "Invalid arXiv link or ID")
        return redirect("collections_list", collection_type="arxiv")

    if ArxivPaper.objects.filter(arxiv_id=arxiv_id).exists():
        messages.warning(request, "This paper is already in your list")
        return redirect("collections_list", collection_type="arxiv")

    metadata = fetch_arxiv_metadata(arxiv_id)
    if not metadata:
        messages.error(request, "Could not fetch arXiv metadata")
        return redirect("collections_list", collection_type="arxiv")

    ArxivPaper.objects.create(
        arxiv_id=arxiv_id,
        title=metadata["title"],
        summary=metadata["summary"],
        authors=metadata["authors"],
    )
    messages.success(request, f"Added arXiv paper {arxiv_id}")
    return redirect("collections_list", collection_type="arxiv")


def handle_github_add(request):
    """Handle adding a GitHub repository."""
    repo_url = request.POST.get("item_url", "").strip()

    if not repo_url:
        messages.error(request, "Please enter a GitHub repository link or owner/repo")
        return redirect("collections_list", collection_type="github")

    repo_ref = extract_github_repo_ref(repo_url)
    if not repo_ref:
        messages.error(request, "Invalid GitHub repository reference")
        return redirect("collections_list", collection_type="github")

    full_name = "/".join(repo_ref)
    if GithubRepo.objects.filter(full_name__iexact=full_name).exists():
        messages.warning(request, "This repository is already in your list")
        return redirect("collections_list", collection_type="github")

    repo_info = fetch_github_repo_info(*repo_ref)
    if not repo_info:
        messages.error(request, "Could not fetch repository information")
        return redirect("collections_list", collection_type="github")

    GithubRepo.objects.create(
        full_name=repo_info["full_name"],
        description=repo_info["description"],
        stars=repo_info["stars"],
        language=repo_info["language"],
        homepage=repo_info["homepage"],
    )
    messages.success(request, f"Added {repo_info['full_name']}")
    return redirect("collections_list", collection_type="github")


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


def extract_arxiv_id(value):
    """Extract arXiv ID from various link formats."""
    value = value.strip()
    print(f"Attempting to extract arXiv ID from: {value}")

    if not value:
        print("❌ Empty value provided")
        return None

    # If it's already an ID
    if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", value):
        print(f"✓ Direct arXiv ID detected: {value}")
        return value

    parsed = urlparse(value)
    path_segments = [seg for seg in parsed.path.split("/") if seg]
    print(f"Parsed URL - netloc: {parsed.netloc}, path segments: {path_segments}")

    if (
        parsed.netloc
        and "arxiv.org" in parsed.netloc
        and path_segments
        and path_segments[0] in {"abs", "pdf"}
        and len(path_segments) >= 2
    ):
        arxiv_id = path_segments[1]
        if path_segments[0] == "pdf" and arxiv_id.endswith(".pdf"):
            arxiv_id = arxiv_id[:-4]
        arxiv_id = arxiv_id.replace(".pdf", "")
        if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", arxiv_id):
            print(f"✓ Extracted arXiv ID from URL: {arxiv_id}")
            return arxiv_id
        print(f"❌ Extracted ID '{arxiv_id}' doesn't match arXiv ID format")

    print("❌ Could not extract valid arXiv ID")
    return None


def fetch_arxiv_metadata(arxiv_id):
    """Fetch metadata for an arXiv paper."""
    try:
        # Check if SSL verification should be disabled (for development/proxy issues)
        verify_ssl = os.getenv("ARXIV_VERIFY_SSL", "true").lower() != "false"

        # Suppress SSL warnings if verification is disabled
        if not verify_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            print("Warning: SSL verification disabled for arXiv API")

        api_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        print(f"Fetching arXiv metadata from: {api_url}")
        headers = {"User-Agent": "MindTreeLog/1.0 (Django app)"}
        response = requests.get(api_url, headers=headers, verify=verify_ssl, timeout=10)
        print(f"arXiv API Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ arXiv API error {response.status_code}: {response.text[:200]}")
            return None

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        if entry is None:
            print("❌ arXiv API returned no entry for this ID")
            print(f"Response preview: {response.text[:500]}")
            return None

        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        authors = [author.text.strip() for author in entry.findall("atom:author/atom:name", ns) if author.text]

        print(f"✓ Successfully fetched arXiv paper: {title[:80]}...")
        return {
            "title": title or f"arXiv:{arxiv_id}",
            "summary": summary,
            "authors": ", ".join(authors),
        }
    except ET.ParseError as exc:
        print(f"❌ Failed to parse arXiv XML response: {exc}")
        if "response" in locals():
            print(f"Response text: {response.text[:500]}")
        return None
    except requests.exceptions.SSLError as exc:
        print(f"❌ SSL Error: {exc}")
        print("Try setting ARXIV_VERIFY_SSL=false in .env file (development only)")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"❌ Network error fetching arXiv metadata: {exc}")
        return None
    except Exception as exc:
        print(f"❌ Unexpected error fetching arXiv metadata: {exc}")
        return None


def extract_github_repo_ref(value):
    """Extract owner and repo from GitHub URLs or refs."""
    value = value.strip()
    if not value:
        return None

    if re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", value):
        owner, repo = value.split("/", 1)
        return owner, repo

    parsed = urlparse(value)
    if "github.com" in parsed.netloc:
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2:
            return parts[0], parts[1]
    return None


def fetch_github_repo_info(owner, repo):
    """Fetch repository information from GitHub API."""
    try:
        # Check if SSL verification should be disabled (for development/proxy issues)
        verify_ssl = os.getenv("GITHUB_VERIFY_SSL", "true").lower() != "false"

        # Suppress SSL warnings if verification is disabled
        if not verify_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            print("Warning: SSL verification disabled for GitHub API")

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        print(f"Fetching GitHub repo info from: {api_url}")
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "MindTreeLog/1.0",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print("Using GitHub token for authentication")
        else:
            print("No GitHub token - using unauthenticated requests (rate limited)")

        response = requests.get(api_url, headers=headers, verify=verify_ssl, timeout=10)
        print(f"GitHub API Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ GitHub API error {response.status_code}: {response.text[:200]}")
            return None

        data = response.json()
        print(f"✓ Successfully fetched GitHub repo: {data.get('full_name')}")
        return {
            "full_name": data.get("full_name", f"{owner}/{repo}"),
            "description": data.get("description") or "",
            "stars": data.get("stargazers_count", 0),
            "language": data.get("language") or "",
            "homepage": data.get("homepage") or "",
        }
    except requests.exceptions.SSLError as exc:
        print(f"❌ SSL Error: {exc}")
        print("Try setting GITHUB_VERIFY_SSL=false in .env file (development only)")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"❌ Network error fetching GitHub repo info: {exc}")
        return None
    except Exception as exc:
        print(f"❌ Unexpected error fetching GitHub repo info: {exc}")
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

    return None


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


def arxiv_delete(request, paper_id):
    """Delete an arXiv paper from the list."""
    try:
        paper = ArxivPaper.objects.get(id=paper_id)
        paper.delete()
        messages.success(request, f"Deleted arXiv:{paper.arxiv_id}")
    except ArxivPaper.DoesNotExist:
        messages.error(request, "Paper not found")
    return redirect("collections_list", collection_type="arxiv")


def arxiv_resync(request, paper_id):
    """Refresh metadata for an arXiv paper."""
    try:
        paper = ArxivPaper.objects.get(id=paper_id)
        metadata = fetch_arxiv_metadata(paper.arxiv_id)
        if metadata:
            paper.title = metadata["title"]
            paper.summary = metadata["summary"]
            paper.authors = metadata["authors"]
            paper.save()
            messages.success(request, f"Resynced arXiv:{paper.arxiv_id}")
        else:
            messages.error(request, "Could not fetch arXiv metadata")
    except ArxivPaper.DoesNotExist:
        messages.error(request, "Paper not found")
    return redirect("collections_list", collection_type="arxiv")


def github_delete(request, repo_id):
    """Delete a GitHub repository from the list."""
    try:
        repo = GithubRepo.objects.get(id=repo_id)
        repo.delete()
        messages.success(request, f"Deleted {repo.full_name}")
    except GithubRepo.DoesNotExist:
        messages.error(request, "Repository not found")
    return redirect("collections_list", collection_type="github")


def github_resync(request, repo_id):
    """Refresh metadata for a GitHub repository."""
    try:
        repo = GithubRepo.objects.get(id=repo_id)
        owner, name = repo.full_name.split("/", 1)
        repo_info = fetch_github_repo_info(owner, name)
        if repo_info:
            repo.description = repo_info["description"]
            repo.stars = repo_info["stars"]
            repo.language = repo_info["language"]
            repo.homepage = repo_info["homepage"]
            repo.save()
            messages.success(request, f"Resynced {repo.full_name}")
        else:
            messages.error(request, "Could not fetch repository info")
    except (GithubRepo.DoesNotExist, ValueError):
        messages.error(request, "Repository not found")
    return redirect("collections_list", collection_type="github")
