from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, CustomLogoutView


urlpatterns = [
    path('', views.dashboard, name='home'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('previous_quizzes/', views.previous_quizzes, name='previous_quizzes'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
