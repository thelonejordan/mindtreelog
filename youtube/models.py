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
