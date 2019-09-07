from unittest import skip

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from ..views.movies import post_movies
from ..models import Movie
from .test_resources import MockMovieDetailsProvider, get_expected_api_response, \
    get_saved_test_movie


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
            expected_response["Id"] = movie.pk
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
        expected_response["Id"] = Movie.objects.first().pk
        self.assertDictEqual(json.loads(another_response.content), expected_response)

    def test_movies_get(self):
        """ If GET request is received, list of all movies should be returned. """
        movie = get_saved_test_movie()
        response = self.client.get(self.get_url(), format='json')
        expected = get_expected_api_response()
        expected["Id"] = movie.pk
        expected = [expected]
        self.assertEqual(json.loads(response.content), expected)

    def test_movies_get_with_multiple(self):
        """ If GET request is received, list of all movies should be returned. """
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        response = self.client.get(self.get_url(), format='json')
        expected = [get_expected_api_response(), get_expected_api_response()]
        expected[0]["Id"] = movie.pk
        expected[1]["Id"] = another_movie.pk
        self.assertEqual(json.loads(response.content), expected)

    def test_movies_get_with_title_sorting(self):
        """ If GET request is received with sort flag set to "Title",
        list of all movies should be returned, sorted by movie title. """
        titles = ["Bcd", "Abc", "Bde"]
        movie = get_saved_test_movie()
        movie.title = titles[0]
        movie.save()
        second_movie = get_saved_test_movie()
        second_movie.title = titles[1]
        second_movie.save()
        third_movie = get_saved_test_movie()
        third_movie.title = titles[2]
        third_movie.save()
        movies = [movie, second_movie, third_movie]
        response = self.client.get(f"{self.get_url()}?sort=Title", format='json')
        expected = [get_expected_api_response(), get_expected_api_response(),
                    get_expected_api_response()]
        for ex_mv, mv in zip(expected, sorted(movies, key=lambda m: m.title)):
            ex_mv["Title"] = mv.title
            ex_mv["Id"] = mv.pk
        self.assertEqual(json.loads(response.content), expected)

    def test_movies_get_with_year_sorting(self):
        """ If GET request is received with sort flag set to "Year", list
        of all movies should be returned, sorted by movie year release. """
        years = [2019, 1987, 2010]
        movie = get_saved_test_movie()
        movie.year = years[0]
        movie.save()
        second_movie = get_saved_test_movie()
        second_movie.year = years[1]
        second_movie.save()
        third_movie = get_saved_test_movie()
        third_movie.year = years[2]
        third_movie.save()
        response = self.client.get(f"{self.get_url()}?sort=Year", format='json')
        expected = [get_expected_api_response(), get_expected_api_response(),
                    get_expected_api_response()]
        movies = [movie, second_movie, third_movie]
        for ex_mv, mv in zip(expected, sorted(movies, key=lambda m: m.year)):
            ex_mv["Year"] = str(mv.year)
            ex_mv["Id"] = mv.pk
        self.assertEqual(json.loads(response.content), expected)

    @skip("Dependent on external calls. Can be run as a sanity check once in a while.")
    def test_response_after_first_movie_post_with_external_call(self):
        """ If movie title is POSTed for the first time object should be created
            and movie details with it's ID should be sent in response """
        data = {'title': 'Shrek'}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        try:
            movie = Movie.objects.get(title="Shrek")
            self.assertEqual(json.loads(response.content).get("Id"), movie.pk)
            self.assertEqual(json.loads(response.content).get("Year"), "2001")
            self.assertEqual(json.loads(response.content).get("Genre"),
                             "Animation, Adventure, Comedy, Family, Fantasy")
            self.assertEqual(json.loads(response.content).get("Awards"),
                             "Won 1 Oscar. Another 36 wins & 60 nominations.")
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
