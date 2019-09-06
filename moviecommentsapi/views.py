from datetime import datetime

import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.utils import json

from .models import Movie, Comment
from .serializers import MovieSerializer, CommentSerializer


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
        return get_comments(request)
    elif request.method == 'POST':
        return post_comments(request)


def get_comments(request):
    if "Id" in request.query_params:
        return get_comments_for_movie(request.query_params.get("Id"))
    else:
        return get_all_comments()


def get_all_comments():
    cs = CommentSerializer(Comment.objects.all(), many=True)
    return JsonResponse(cs.data, status=status.HTTP_200_OK, safe=False)


def get_comments_for_movie(movie_id):
    try:
        movie = Movie.objects.get(pk=movie_id)
        cmnts = Comment.for_movie(movie)
        cs = CommentSerializer(cmnts, many=True)
        return JsonResponse(cs.data, status=status.HTTP_200_OK, safe=False)
    except Movie.DoesNotExist:
        return JsonResponse({"message": "movie with given id not found"},
                            status=status.HTTP_404_NOT_FOUND)


def post_comments(request):
    movie_id = request.data.get("Id")
    try:
        movie = Movie.objects.get(pk=movie_id)
        comment = movie.comments.create(text=request.data.get("Text"))
        cs = CommentSerializer(comment)
        return JsonResponse(cs.data, status=status.HTTP_201_CREATED)
    except Movie.DoesNotExist:
        return JsonResponse({"message": "movie with given id not found"},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def top(request):
    if all(param in request.query_params for param in ("From", "To")):
        date_from, date_to = request.query_params.get("From"), request.query_params.get("To")
        date_from, date_to = datetime.strptime(date_from, '%d %b %Y'), datetime.strptime(date_to,
                                                                                         '%d %b %Y')
        return JsonResponse(get_ranking(date_from, date_to), safe=False)
    else:
        return JsonResponse({"message": "no date range provided"},
                            status=status.HTTP_400_BAD_REQUEST)


def get_ranking(date_from, date_to):
    cmnts = Comment.in_range(date_from, date_to)
    mvs = list(set([comment.movie_id for comment in cmnts]))
    ranking = list()
    for movie in mvs:
        ranking.append({"MovieId": movie.pk,
                        "TotalComments": Comment.sum_for_movie_in_range(movie, date_from, date_to)})
    ranking.sort(key=lambda m: m["MovieId"])
    ranking.sort(key=lambda m: m["TotalComments"], reverse=True)
    rank = 1
    for i, movie in enumerate(ranking):
        movie.update({"Rank": rank})
        if i+1 <= (len(ranking)-1) and movie["TotalComments"] != ranking[i + 1]["TotalComments"]:
                rank += 1
    return ranking


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
