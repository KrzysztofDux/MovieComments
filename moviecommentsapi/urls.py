from django.urls import path

from .views.movies import movies
from .views.comments import comments
from .views.others import top

app_name = 'moviecommentsapi'
urlpatterns = [
    path('movies/', movies, name='movies'),
    path('comments/', comments, name='comments'),
    path('top/', top, name='top'),
]
