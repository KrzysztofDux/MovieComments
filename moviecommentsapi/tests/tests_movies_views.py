from unittest import skip

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from ..views.movies import post_movies
from ..models import Movie
from .test_resources import MockMovieDetailsProvider, get_expected_api_response, get_saved_test_movie


class MoviesViewTests(APITestCase):
    maxDiff = None

    @staticmethod
    def get_url():
        return '/movies/'

    def test_movie_creation_after_post(self):
        """ If movie title is POSTed for the first time object should be created. """
        data = {'title': 'It'}
        post_movies(MockRequest(data), MockMovieDetailsProvider())
        self.assertEqual(len(Movie.objects.all()), 1)
        try:
            Movie.objects.get(title="It")
        except Movie.DoesNotExist:
            self.fail(msg="Movie with proper title was not created.")
        except Movie.MultipleObjectsReturned:
            self.fail(msg="Movie with given title was created multiple times.")

    def test_response_after_first_movie_post(self):
        """ If movie title is POSTed for the first time object should be created
            and movie details with it's ID should be sent in response. """
        data = {'title': 'It'}
        expected_response = get_expected_api_response()
        response = post_movies(MockRequest(data), MockMovieDetailsProvider())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        try:
            movie = Movie.objects.get(title="It")
            expected_response["Id"] = str(movie.pk)
            self.assertEqual(json.loads(response.content), expected_response)
        except Movie.DoesNotExist:
            self.fail(msg="Movie with proper title was not created.")
        except Movie.MultipleObjectsReturned:
            self.fail(msg="Movie with given title was created multiple times.")

    def test_response_after_another_movie_post(self):
        """ If movie with title provided in POST request already exists
            in the database it's details and ID should be sent in response. """
        data = {'title': 'It'}
        expected_response = get_expected_api_response()
        first_response = post_movies(MockRequest(data), MockMovieDetailsProvider())
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        another_response = post_movies(MockRequest(data), MockMovieDetailsProvider())
        self.assertEqual(another_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Movie.objects.all()), 1)
        expected_response["Id"] = str(Movie.objects.first().pk)
        self.assertDictEqual(json.loads(another_response.content), expected_response)

    def test_movies_get(self):
        """ If GET request is received, list of all movies should be returned. """
        movie = get_saved_test_movie()
        response = self.client.get(self.get_url(), format='json')
        try:
            expected = get_expected_api_response()
            expected["Id"] = str(movie.pk)
            expected = [expected]
            self.assertEqual(json.loads(response.content), expected)
        except KeyError:
            "Id not set"

    @skip("Dependent on external calls. Can be run as a sanity check once in a while.")
    def test_response_after_first_movie_post_with_external_call(self):
        """ If movie title is POSTed for the first time object should be created
            and movie details with it's ID should be sent in response """
        data = {'title': 'Shrek'}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        try:
            movie = Movie.objects.get(title="Shrek")
            self.assertEqual(json.loads(response.content).get("Id"), str(movie.pk))
            self.assertEqual(json.loads(response.content).get("Year"), "2001")
            self.assertEqual(json.loads(response.content).get("Genre"), "Animation, Adventure, Comedy, Family, Fantasy")
            self.assertEqual(json.loads(response.content).get("Awards"), "Won 1 Oscar. Another 36 wins & 60 nominations.")
            self.assertEqual(json.loads(response.content).get("Runtime"), "90 min")
        except Movie.DoesNotExist:
            self.fail(msg="Movie with proper title was not created.")
        except Movie.MultipleObjectsReturned:
            self.fail(msg="Movie with given title was created multiple times.")

    @skip("Dependent on external calls. Can be run as a sanity check once in a while.")
    def test_response_after_first_movie_post_with_two_external_calls(self):
        """ If movie with title provided in POST request already exists
            in the database it's details and ID should be sent in response. """
        data = {'title': 'The Room'}
        first_response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        another_response = post_movies(MockRequest(data), MockMovieDetailsProvider())
        self.assertEqual(another_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Movie.objects.all()), 1)
        self.assertEqual(json.loads(another_response.content).get("Title"), "The Room")
        self.assertEqual(json.loads(another_response.content).get("Metascore"), "9")


class MockRequest:
    """ To make tests independent from external api
    no real POST request to "movies" endpoint is sent. """
    def __init__(self, data):
        self.data = data
