import requests

from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.utils import json

from ..models import Movie
from ..serializers import MovieSerializer


@api_view(['GET', 'POST'])
def movies(request):
    if request.method == 'GET':
        return get_movies(request)
    elif request.method == 'POST':
        details_provider = OMDbDetailsProvider()
        return post_movies(request, details_provider)


def get_movies(request):
    mvs = MovieSerializer(Movie.objects.all(), many=True).data
    sort_key = get_sorter(request.query_params)
    if sort_key:
        mvs.sort(key=sort_key)
    return JsonResponse(mvs, status=status.HTTP_200_OK, safe=False)


def get_sorter(query_params):
    param = query_params.get("sort")
    year_flags = ("year", "Year", "y", "Y")
    title_flags = ("title", "Title", "t", "T")
    both_flags = [f"{y}{t}" for y, t in zip(year_flags, title_flags)]
    if param in both_flags:
        return lambda m: (m["Year"], m["Title"])
    elif param in year_flags:
        return lambda m: m["Year"]
    elif param in title_flags:
        return lambda m: m["Title"]
    return False


def post_movies(request, details_provider):
    try:
        title = request.data["title"].strip()
        return get_movie_by_title(title, details_provider)
    except KeyError:
        return JsonResponse({"message": "no movie title provided"},
                            status=status.HTTP_400_BAD_REQUEST)
    except (APIException, ConnectionError) as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Movie.DuplicateError:
        """ if movie exists in database, but was requested
        with different version or spelling of title """
        formal_title = details_provider.get_formal_title(title)
        return get_movie_by_title(formal_title, details_provider)


def get_formal_title(title):
    provider = OMDbDetailsProvider()
    details = provider.get_details(title)
    return details["Title"]


def get_movie_by_title(title, details_provider):
    if Movie.objects.filter(title__iexact=title).exists():
        return handle_existing_movie(title)
    else:
        return handle_new_movie(title, details_provider)


def handle_existing_movie(title):
    movie = Movie.objects.filter(title__iexact=title).get()
    ms = MovieSerializer(movie)
    return JsonResponse(ms.data, status=status.HTTP_200_OK)


def handle_new_movie(title, details_provider):
    movie = Movie.create(title, details_provider)
    ms = MovieSerializer(movie)
    return JsonResponse(ms.data, status=status.HTTP_201_CREATED)


class OMDbDetailsProvider(Movie.AbstractDetailsProvider):
    def __init__(self):
        self.__details = None

    def get_details(self, title):
        """ Getting details lazily to avoid unnecessary or multiple calls. """
        if self.__details:
            return self.__details
        else:
            response = requests.get(settings.OMDB_URL, {"apikey": settings.OMDB_KEY, "t": title})
            response_json = json.loads(response.text)
            if response_json.get("Response") == 'True':
                self.__details = json.loads(response.text)
                return self.__details
            elif response_json.get("Response") == 'False':
                raise APIException(response_json.get("Error"))
            else:
                raise APIException("problem with external API occurred")

    def get_formal_title(self, title):
        return self.get_details(title).get("Title")

    def get_serializer(self, **kwargs):
        return MovieSerializer(**kwargs)
