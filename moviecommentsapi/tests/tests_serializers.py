import datetime
from itertools import zip_longest

from django.test import TestCase

from .test_resources import get_expected_api_response, get_expected_external_api_response, \
    get_saved_test_movie
from ..serializers import MovieSerializer, CommentSerializer


class MovieSerializerTests(TestCase):
    maxDiff = None

    def test_movie_serialization(self):
        """ MovieSerializer provided Movie object should be JSONable into given format. """
        movie = get_saved_test_movie()
        ms = MovieSerializer(movie)
        expected = get_expected_api_response()
        expected["Id"] = movie.pk
        self.assertEqual(ms.data, expected)

    def test_movie_deserialization(self):
        """ MovieSerializer provided JSON api response should create Movie object
            with correct attributes values and related Rating objects """
        ms = MovieSerializer(data=get_expected_external_api_response())
        ms.is_valid()
        movie = ms.save()
        expected = get_saved_test_movie()
        self.movie_attributes_check(movie, expected)
        self.movie_ratings_check(movie, expected)

    def movie_attributes_check(self, result, expected):
        movie_attrs = ["title", "year", "rated", "released", "runtime", "genre", "director",
                       "writer", "actors", "plot", "language", "country", "awards", "poster",
                       "metascore", "imdb_rating", "imdb_votes", "imdb_id", "type", "dvd",
                       "box_office", "production", "website"]
        for m in movie_attrs:
            try:
                self.assertEqual(getattr(result, m), getattr(expected, m))
            except AttributeError:
                self.fail(f"movie has no attribute {m}")

    def movie_ratings_check(self, result, expected):
        for er, rr in zip_longest(expected.ratings.all(), result.ratings.all()):
            try:
                self.assertEqual(rr.source, er.source)
                self.assertEqual(rr.value, er.value)
            except AttributeError:
                self.fail("rating lists uneven or incorrectly populated")


class CommentSerializerTests(TestCase):

    def test_comment_serialization(self):
        movie = get_saved_test_movie()
        comment = movie.comments.create(text="test comment")
        comment.created_date = datetime.date(2019, 3, 10)
        comment.save()
        cs = CommentSerializer(comment)
        expected = {"MovieId": movie.pk, "Text": "test comment", "CreatedDate": "10 Mar 2019"}
        self.assertEqual(cs.data, expected)

    def test_comment_deserialization(self):
        movie = get_saved_test_movie()
        comment_serialized = {"MovieId": movie.pk, "Text": "test comment",
                              "CreatedDate": "10 Mar 2019"}
        cs = CommentSerializer(data=comment_serialized)
        cs.is_valid()
        comment = cs.save()
        self.assertEqual(comment.movie.pk, comment_serialized["MovieId"])
        self.assertEqual(comment.text, comment_serialized["Text"])
        self.assertEqual(comment.created_date.strftime('%d %b %Y'),
                         comment_serialized["CreatedDate"])
