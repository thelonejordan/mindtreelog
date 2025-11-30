from django.contrib import admin

from .models import ArxivPaper, GithubRepo, TwitterPost, YouTubeVideo


# Register your models here.
@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "video_id")
    search_fields = ("title", "video_id")


@admin.register(TwitterPost)
class TwitterPostAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_handle", "post_id", "text_preview")
    search_fields = ("author_name", "author_handle", "text", "post_id")
    list_filter = ("author_handle",)

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Text Preview"


@admin.register(ArxivPaper)
class ArxivPaperAdmin(admin.ModelAdmin):
    list_display = ("arxiv_id", "title", "authors")
    search_fields = ("arxiv_id", "title", "authors")


@admin.register(GithubRepo)
class GithubRepoAdmin(admin.ModelAdmin):
    list_display = ("full_name", "stars", "language")
    search_fields = ("full_name", "language")
    list_filter = ("language",)
