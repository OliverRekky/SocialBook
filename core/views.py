from django.shortcuts import render, redirect
from .forms import CreateUserForm, ProfileForm, PostForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from itertools import chain
from django.db.models import Q
import random
from .models import *

# Create your views here.

@login_required(login_url='login')
def index(request):
	posts = Post.objects.all().order_by('-created_at')

	user_following_list = []
	feed = []

	user_following = FollowerCount.objects.filter(followers=request.user.profile).order_by('-id')

	for users in user_following:
		user_following_list.append(users.user)

	for usernames in user_following_list:
		feed_lists = Post.objects.filter(user__user__username=usernames).order_by('-created_at')
		feed.append(feed_lists)

	feed_list = list(chain(*feed))


	all_users = User.objects.all()
	user_following_all = []

	for user in user_following:
		user_list = User.objects.get(username=user.user)
		user_following_all.append(user_list)

	new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
	current_user = User.objects.filter(username=request.user.username)
	final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
	random.shuffle(final_suggestions_list)
	
	username_profile = []
	username_profile_list = []

	for users in final_suggestions_list:
		username_profile.append(users.username)

	for usernames in username_profile:
		profile_lists = Profile.objects.filter(user__username=usernames)
		username_profile_list.append(profile_lists)

	suggestions_username_profile_list = list(chain(*username_profile_list))

	user = request.user.profile
	form = PostForm()
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			Post.objects.create(
				user=user,
				post_img=form.cleaned_data['post_img'],
				caption=form.cleaned_data['caption'],
				)
			return redirect('index')

	context = {'posts': feed_list, 'form': form,
	 'suggestions_username_profile_list':suggestions_username_profile_list[:4]}
	return render(request, 'core/index.html', context)


def registerPage(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				user = form.save()
				username = form.cleaned_data.get('username')

				#log in
				user_login = authenticate(
					username=form.cleaned_data['username'],
					password=form.cleaned_data['password1']
					)
				login(request, user_login)

				Profile.objects.create(
					user=user,
					)
				return redirect('index')
			else:
				messages.error(request,'An error occurred during registration')

	context = {'form': form}
	return render(request, 'core/register.html', context)



def loginPage(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:	
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('index')
			else:
				messages.info(request, "Username or password is incorrect")	
		context ={}
		return render(request, 'core/login.html', context)


@login_required(login_url='login')
def logoutPage(request):
	logout(request)
	return redirect('index')


@login_required(login_url='login')
def settingsPage(request):
	user = request.user.profile
	form = ProfileForm(instance=user)

	if request.method == 'POST':
		form = ProfileForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			form.save()
			messages.success(request, "Profile updated successfully")
			return redirect('settings')

	context = {'form':form}
	return render(request, 'core/setting.html', context)


@login_required(login_url='login')
def likePost(request):
	username = request.user.username
	id_post = request.GET.get('post_id')

	post = Post.objects.get(post_id=id_post)

	like_filter = LikePost.objects.filter(id_post=id_post, username=username).first()

	if like_filter == None:
		new_like = LikePost.objects.create(username=username, id_post=id_post)
		new_like.save()
		post.no_of_likes = post.no_of_likes + 1
		post.save()
		return redirect('/')
	else: 
		like_filter.delete() 
		post.no_of_likes = post.no_of_likes - 1 
		post.save()
		return redirect('/')


@login_required(login_url='login')
def profilePage(request, pk):
	users = Profile.objects.get(id=pk)
	posts = Post.objects.filter(user=users)
	posts_count = posts.count()

	follower = request.user.profile
	user_follow = users.user
	followers = FollowerCount.objects.filter(user=users.user).count()
	following = FollowerCount.objects.filter(followers=users.user).count()

	if FollowerCount.objects.filter(user=user_follow, followers=follower).first():
		button_text = 'Unfollow'
	else:
		button_text = 'Follow'

	context = {'user': users, 'posts': posts,
	 'posts_count': posts_count, 'button_text':button_text,
	 'followers':followers,'following':following
	 }
	return render(request, 'core/profile.html', context)



@login_required(login_url='login')
def followAction(request):
	if request.method == 'POST':
		follower = request.POST.get('follower')
		user = request.POST.get('user')
		id_profile = request.POST.get('id')
		if FollowerCount.objects.filter(followers=follower, user=user).first():
			delete_follower = FollowerCount.objects.get(user=user, followers=follower)
			delete_follower.delete()
			return redirect('profile', pk=id_profile)
		else:
			new_follower = FollowerCount.objects.create(user=user, followers=follower)
			new_follower.save()
			return redirect('profile', pk=id_profile)



@login_required(login_url='login')
def searchAction(request):
	q = request.GET.get('q') if request.GET.get('q') != None else ''

	users = Profile.objects.filter(
		Q(user__username__icontains=q) |
		Q(bio__icontains=q)|
		Q(location__icontains=q)
		)
	context = {'users': users}
	return render(request, 'core/search.html', context)