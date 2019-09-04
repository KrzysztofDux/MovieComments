from rest_framework import status
from rest_framework.test import APITestCase
from .models import Movie, Rating
from .test_resources import MockMovieDetailsProvider, expected_api_response, save_test_movie


class MoviesViewTests(APITestCase):

    @staticmethod
    def get_url():
        return '/movies'

    def setUp(self):
        """ mocking details provider makes tests independent from external API """
        details_provider = MockMovieDetailsProvider()
        Movie.default_detail_provider = details_provider

    def test_movie_creation_after_post(self):
        """ If movie title is POSTed for the first time object should be created. """
        data = {'title': 'It'}
        self.client.post(self.get_url(), data, format='json')
        self.assertEqual(len(Movie.objects.all()), 1)
        try:
            Movie.objects.get(title="It")
        except Movie.DoesNotExist:
            self.fail(msg="Movie with proper title was not created.")
        except Rating.MultipleObjectsReturned:
            self.fail(msg="Movie with given title was created multiple times.")

    def test_response_after_first_movie_post(self):
        """ If movie title is POSTed for the first time object should be created
            and movie details with it's ID should be sent in response. """
        data = {'title': 'It'}
        expected_response = expected_api_response
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        try:
            Movie.objects.get(title="It")
            self.assertDictEqual(response.data, expected_response)
        except Movie.DoesNotExist:
            self.fail(msg="Movie with proper title was not created.")
        except Rating.MultipleObjectsReturned:
            self.fail(msg="Movie with given title was created multiple times.")

    def test_response_after_another_movie_post(self):
        """ If movie with title provided in POST request already exists
            in the database it's details and ID should be sent in response. """
        data = {'title': 'It'}
        expected_response = expected_api_response
        first_response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        another_response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(another_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(Movie.objects.all()), 1)
        self.assertDictEqual(another_response.data, expected_response)

    def test_movies_get(self):
        """ If GET request is received, list of all movies should be returned. """
        save_test_movie()
        response = self.client.get(self.get_url(), format='json')
        self.assertEqual(response.data, expected_api_response)
