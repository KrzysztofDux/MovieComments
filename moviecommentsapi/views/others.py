from datetime import datetime

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models import Movie, Comment


@api_view(['GET'])
def top(request):
    if all(param in request.query_params for param in ("from", "to")):
        date_from, date_to = request.query_params.get("from"), request.query_params.get("to")
        date_from, date_to = datetime.strptime(date_from, '%d %b %Y'), datetime.strptime(date_to,
                                                                                         '%d %b %Y')
        return JsonResponse(get_ranking(date_from, date_to), safe=False)
    else:
        return JsonResponse({"message": "no date range provided"},
                            status=status.HTTP_400_BAD_REQUEST)


def get_ranking(date_from, date_to):
    cmnts = Comment.in_range(date_from, date_to)
    mvs = list(set([comment.movie for comment in cmnts]))
    ranking = list()
    for movie in mvs:
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
