from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view

from ..models import Movie, Comment
from ..serializers import CommentSerializer


@api_view(['GET', 'POST'])
def comments(request):
    if request.method == 'GET':
        return get_comments(request)
    elif request.method == 'POST':
        return post_comments(request)


def get_comments(request):
    if "id" in request.query_params:
        return get_comments_for_movie(request.query_params.get("id"))
    else:
        return get_all_comments()


def get_comments_for_movie(movie_id):
    try:
        movie = Movie.objects.get(pk=movie_id)
        cmnts = Comment.for_movie(movie)
        cs = CommentSerializer(cmnts, many=True)
        return JsonResponse(cs.data, status=status.HTTP_200_OK, safe=False)
    except Movie.DoesNotExist:
        return JsonResponse({"message": "movie with given id not found"},
                            status=status.HTTP_404_NOT_FOUND)


def get_all_comments():
    cs = CommentSerializer(Comment.objects.all(), many=True)
    return JsonResponse(cs.data, status=status.HTTP_200_OK, safe=False)


def post_comments(request):
    try:
        return create_comment(request)
    except Movie.DoesNotExist:
        return JsonResponse({"message": "movie with given id not found"},
                            status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        return JsonResponse({"message": "no movie id provided"}, status=status.HTTP_400_BAD_REQUEST)


def create_comment(request):
    movie_id = request.data["id"]
    movie = Movie.objects.get(pk=movie_id)
    comment = movie.comments.create(text=request.data["text"])
    cs = CommentSerializer(comment)
    return JsonResponse(cs.data, status=status.HTTP_201_CREATED)
