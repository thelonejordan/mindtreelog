from django.urls import path

from collectibles import views

urlpatterns = [
    path("list", views.video_list, name="list"),
    path("video/<int:video_id>/delete", views.video_delete, name="video_delete"),
    path("video/<int:video_id>/resync", views.video_resync, name="video_resync"),
    path("xlist", views.twitter_list, name="xlist"),
    path("post/<int:post_id>/delete", views.twitter_delete, name="twitter_delete"),
    path("post/<int:post_id>/resync", views.twitter_resync, name="twitter_resync"),
    path("", views.home, name="home"),
]
