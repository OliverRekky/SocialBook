from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.


class Profile(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	bio = models.TextField(blank=True)
	profileimg = models.ImageField(null=True, default='user.png')
	location = models.CharField(max_length=100, blank=True)


	@property
	def imageURL(self):
		try:
			url = self.profileimg.url
		except:
			url = ''
		return url

	def __str__(self):
		return str(self.user.username)



class Post(models.Model):
	post_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	user = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)
	post_img = models.ImageField(null=True, blank=True)
	caption = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	no_of_likes = models.IntegerField(default=0)


	@property
	def postImageURL(self):
		try:
			url = self.post_img.url
		except:
			url = ''
		return url


	def __str__(self):
		return str(self.user)


class LikePost(models.Model):
	id_post = models.CharField(max_length=500)
	username = models.CharField(max_length=100)

	def __str__(self):
		return str(self.username)


class FollowerCount(models.Model):
	user = models.CharField(max_length=100)
	followers = models.CharField(max_length=100)


	def __str__(self):
		return str(self.user)