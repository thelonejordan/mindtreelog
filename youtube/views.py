from django.shortcuts import render
from django.http import HttpResponse
from .models import YouTubeVideo


def home(request):  
    return HttpResponse("Hello, Django!")


def video_list(request):
    videos = YouTubeVideo.objects.all()
    return render(request, "youtube/video_list.html", {"videos": videos})
