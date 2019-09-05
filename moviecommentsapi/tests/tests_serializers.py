from itertools import zip_longest

from django.test import TestCase
from rest_framework.utils import json

from .test_resources import expected_api_response, expected_external_api_response, get_saved_test_movie
from ..serializers import MovieSerializer


class MovieSerializerTests(TestCase):

    maxDiff = None

    def test_movie_serialization(self):
        movie = get_saved_test_movie()
        movie.save()
        ms = MovieSerializer(movie)
        expected = json.dumps(expected_api_response)
        result = json.dumps(ms.data)
        self.assertEqual(json.dumps(expected_api_response), json.dumps(ms.data))

    def test_movie_deserialization(self):
        ms = MovieSerializer(data=expected_external_api_response)
        ms.is_valid()
        movie = ms.save()
        expected = get_saved_test_movie()
        movie_attrs = ["title", "year", "rated", "released", "runtime", "genre", "director",
                       "writer", "actors", "plot", "language", "country", "awards", "poster",
                       "metascore", "imdb_rating", "imdb_votes", "imdb_id", "type", "dvd",
                       "box_office", "production", "website"]
        for m in movie_attrs:
            try:
                self.assertEqual(getattr(movie, m), getattr(expected, m))
            except AttributeError:
                self.fail(f"movie has no attribute {m}")
        for er, rr in zip_longest(expected.ratings.all(), movie.ratings.all()):
            try:
                self.assertEqual(rr.source, er.source)
                self.assertEqual(rr.value, er.value)
            except AttributeError:
                self.fail("rating lists uneven or incorrectly populated")
