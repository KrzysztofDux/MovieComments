import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.utils import json

from .models import Movie
from .serializers import MovieSerializer


@api_view(['GET', 'POST'])
def movies(request):
    if request.method == 'GET':
        return get_movies(request)
    elif request.method == 'POST':
        details_provider = OMDbDetailsProvider()
        return post_movies(request, details_provider)


def get_movies(request):
    ms = MovieSerializer(Movie.objects.all(), many=True)
    return JsonResponse(ms.data, status=status.HTTP_200_OK, safe=False)


def post_movies(request, details_provider):
    title = request.data.get("title")
    if Movie.objects.filter(title__iexact=title).exists():
        movie = Movie.objects.get(title=title)
        ms = MovieSerializer(movie)
        return JsonResponse(ms.data, status=status.HTTP_200_OK)
    else:
        movie = Movie.create(title, details_provider)
        ms = MovieSerializer(movie)
        return JsonResponse(ms.data, status=status.HTTP_201_CREATED)


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


class OMDbDetailsProvider:
    def get_details(self, title):
        response = requests.get(settings.OMDB_URL, {"apikey": settings.OMDB_KEY, "t": title})
        response_json = json.loads(response.text)
        if response_json.get("Response") == 'True':
            return json.loads(response.text)
        elif response_json.get("Response") == 'False':
            raise APIException(response_json.get("Error"))
        else:
            raise APIException("problem with external API occurred")
