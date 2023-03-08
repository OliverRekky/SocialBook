from django.urls import path
from . import views


urlpatterns = [
	path('', views.index, name='index'),
	path('register/', views.registerPage, name='register'),
	path('login/', views.loginPage, name='login'),
	path('logout/', views.logoutPage, name='logout'),

	path('settings/', views.settingsPage, name='settings'),


	path('like-post/', views.likePost, name='like'),

	path('profile/<str:pk>', views.profilePage, name='profile'),

	path('follow', views.followAction, name='follow'),

	path('search', views.searchAction, name='search'),
]