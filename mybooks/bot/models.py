from django.db import models


class Chat(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('banned', 'Banned')]

    chat_id = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    is_bot = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return str(self.chat_id)


class Media(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]
    TYPE_CHOICES = [('book', 'Book'), ('podcast', 'Podcast'), ('music', 'Music'), ('photo', 'Photo')]

    file_id = models.CharField(max_length=256, unique=True)
    file_name = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=256, blank=True, null=True)
    author = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type_of_media = models.CharField(max_length=10, choices=TYPE_CHOICES, default='book')
    views_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')

    def __str__(self):
        return str(self.file_id)


class Ad(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to='ads')
    caption = models.TextField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')

    def __str__(self):
        return str(self.title)
