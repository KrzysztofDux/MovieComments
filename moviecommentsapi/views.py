from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Movie
from .serializers import MovieSerializer


@api_view(['GET', 'POST'])
def movies(request):
    if request.method == 'GET':
        return get_movies(request)
    elif request.method == 'POST':
        return post_movies(request)


def get_movies(request):
    ms = MovieSerializer(Movie.objects.all(), many=True)
    return JsonResponse(ms.data, status=status.HTTP_200_OK, safe=False)


def post_movies(request):
    pass


@api_view(['GET', 'POST'])
def comments(request):
    if request.method == 'GET':
        return get_movies(request)
    elif request.method == 'POST':
        return post_movies(request)


def get_comments(request):
    pass


def post_comments(request):
    pass


@api_view(['GET'])
def top(request):
    pass
