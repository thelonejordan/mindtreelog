from django.urls import path

from youtube import views

urlpatterns = [
    path("list", views.video_list, name="list"),
    path("", views.home, name="home"),
]
