from django.urls import path

from . import views

app_name = 'moviecommentsapi'
urlpatterns = [
    path('movies/', views.movies, name='movies'),
    path('comments/', views.comments, name='comments'),
    path('top/', views.top, name='top'),
]
