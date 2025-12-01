from django.db import models


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


class ArxivPaper(models.Model):
    title = models.CharField(max_length=300)
    arxiv_id = models.CharField(max_length=50, unique=True)
    summary = models.TextField(blank=True)
    authors = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = "arxiv_papers"

    def __str__(self):
        return f"{self.arxiv_id}: {self.title[:50]}"

    def paper_url(self):
        return f"https://arxiv.org/abs/{self.arxiv_id}"


class GithubRepo(models.Model):
    full_name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=500, blank=True)
    stars = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=50, blank=True)
    homepage = models.URLField(blank=True)

    class Meta:
        db_table = "github_repos"

    def __str__(self):
        return self.full_name

    def repo_url(self):
        return f"https://github.com/{self.full_name}"


class Link(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "links"

    def __str__(self):
        return f"{self.title[:50]}: {self.url[:50]}"

    def link_url(self):
        return self.url
