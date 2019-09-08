from datetime import datetime

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models import Movie, Comment


@api_view(['GET'])
def top(request):
    try:
        date_from, date_to = request.query_params.get("from"), request.query_params.get("to")
        date_from, date_to = datetime.strptime(date_from, '%d %b %Y'), datetime.strptime(date_to,
                                                                                         '%d %b %Y')
        include_all = include_all_param_to_bool(request.query_params)
        return JsonResponse(get_ranking(date_from, date_to, include_all), safe=False)
    except (KeyError, TypeError):
        return JsonResponse({"message": "no date range provided"},
                            status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return JsonResponse({"message": "wrong date format provided"},
                            status=status.HTTP_400_BAD_REQUEST)


def include_all_param_to_bool(req_params):
    if req_params.get('include_all') in ('True', 'true', 't', 'Yes', 'yes', 'y', '1'):
        return True
    return False


def get_ranking(date_from, date_to, include_all):
    if include_all:
        return prepare_ranking(date_from, date_to, Movie.objects.all())
    comments = Comment.in_range(date_from, date_to)
    movies = list(set([comment.movie for comment in comments]))
    return prepare_ranking(date_from, date_to, movies)


def prepare_ranking(date_from, date_to, movies):
    ranking = list()
    for movie in movies:
        ranking.append({"MovieId": movie.pk,
                        "TotalComments": Comment.sum_for_movie_in_range(movie, date_from, date_to)})
    ranking.sort(key=lambda m: m["MovieId"])
    ranking.sort(key=lambda m: m["TotalComments"], reverse=True)
    rank = 1
    for i, movie in enumerate(ranking):
        movie.update({"Rank": rank})
        is_last_iter = i + 1 <= (len(ranking) - 1)
        if is_last_iter and movie["TotalComments"] != ranking[i + 1]["TotalComments"]:
            rank += 1
    return ranking
