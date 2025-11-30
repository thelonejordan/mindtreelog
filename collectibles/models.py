from django.db import models

# Create your models here.


class YouTubeVideo(models.Model):
    title = models.CharField(max_length=200)
    video_id = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "youtube_videos"

    def __str__(self):
        return self.title

    def thumbnail_url(self):
        return f"https://img.youtube.com/vi/{self.video_id}/hqdefault.jpg"

    def video_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"


class TwitterPost(models.Model):
    text = models.CharField(max_length=500)
    post_id = models.CharField(max_length=30, unique=True)
    author_name = models.CharField(max_length=100)
    author_handle = models.CharField(max_length=50)

    class Meta:
        db_table = "twitter_posts"

    def __str__(self):
        return f"@{self.author_handle}: {self.text[:50]}"

    def post_url(self):
        return f"https://x.com/{self.author_handle}/status/{self.post_id}"

    def embed_url(self):
        """URL format required for Twitter embed widgets"""
        return f"https://twitter.com/{self.author_handle}/status/{self.post_id}?ref_src=twsrc%5Etfw"
