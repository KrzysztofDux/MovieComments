from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Movie, Rating
from .test_resources import expected_external_api_response, expected_api_response, save_test_movie


class MovieModelTests(TestCase):

    def test_movie_create(self):
        """ Testing if movie details are properly mapped. """
        details_provider = MockMovieDetailsProvider()
        details = details_provider.get_details()
        movie_attrs = ["title", "year", "rated", "released", "runtime", "genre", "director",
                       "writer", "actors", "plot", "language", "country", "awards", "poster",
                       "metascore", "imdb_rating", "imdb_votes", "imdb_id", "type", "dvd",
                       "box_office", "production", "website"]
        details_attr = ["Title", "Year", "Rated", "Released", "Runtime", "Genre", "Director",
                        "Writer", "Actors", "Plot", "Language", "Country", "Awards", "poster",
                        "Metascore", "imdbRating", "imdbVotes", "imdbID", "Type", "DVD",
                        "BoxOffice", "Production", "Website"]
        movie = Movie.create("It", details_provider)
        for m, d in zip(movie_attrs, details_attr):
            try:
                movie_attr = getattr(movie, m)
                self.assertEqual(movie_attr, details[d])
            except AttributeError:
                self.fail(f"movie has no attribute {m}")

    def test_related_ratings_after_movie_create(self):
        """ Testing if movie ratings are properly mapped to Rating objects. """
        details_provider = MockMovieDetailsProvider()
        details = details_provider.get_details()
        movie = Movie.create("It", details_provider)
        try:
            r0 = self.get_rating_with_details(details, 0)
            r1 = self.get_rating_with_details(details, 1)
            r2 = self.get_rating_with_details(details, 2)
            self.assertIn(r0, movie.rating_set.all())
            self.assertIn(r1, movie.rating_set.all())
            self.assertIn(r2, movie.rating_set.all())
        except Rating.DoesNotExist:
            self.fail(msg="Rating for movie not created.")
        except Rating.MultipleObjectsReturned:
            self.fail(msg="Rating for movie created more than once.")

    @staticmethod
    def get_rating_with_details(details, index):
        return Rating.object.get(source=details["Ratings"][index]["Source"],
                      value=details["Ratings"][index]["Value"])


class MovieViewTests(APITestCase):

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
        """ If GET request is received list of all movies should be returned. """
        save_test_movie()
        response = self.client.get(self.get_url(), format='json')
        self.assertEqual(response.data, expected_api_response)


class MockMovieDetailsProvider:
    def get_details(self):
        return expected_external_api_response
