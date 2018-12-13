from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Album(models.Model):
	user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
	album_title = models.CharField(max_length=50)
	artist = models.CharField(max_length=25)
	genre = models.CharField(max_length=10)
	cover = models.FileField()
	is_favorite = models.BooleanField(default=False)

	def __str__(self):
		return self.album_title


class Song(models.Model):
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	song_name = models.CharField(max_length=50)
	audio_file = models.FileField()
	is_favorite = models.BooleanField(default=False)

	def __str__(self):
		return self.song_name


