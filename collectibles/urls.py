from django.urls import path

from collectibles import views

urlpatterns = [
    # Unified collections view
    path("collections/<str:collection_type>", views.collections_list, name="collections_list"),
    # Action endpoints
    path("video/<int:video_id>/delete", views.video_delete, name="video_delete"),
    path("video/<int:video_id>/resync", views.video_resync, name="video_resync"),
    path("post/<int:post_id>/delete", views.twitter_delete, name="twitter_delete"),
    path("post/<int:post_id>/resync", views.twitter_resync, name="twitter_resync"),
    path("paper/<int:paper_id>/delete", views.arxiv_delete, name="arxiv_delete"),
    path("paper/<int:paper_id>/resync", views.arxiv_resync, name="arxiv_resync"),
    path("repo/<int:repo_id>/delete", views.github_delete, name="github_delete"),
    path("repo/<int:repo_id>/resync", views.github_resync, name="github_resync"),
    # Legacy redirects (for backward compatibility)
    path("list", views.video_list, name="list"),
    path("xlist", views.twitter_list, name="xlist"),
    # Home
    path("", views.home, name="home"),
]
