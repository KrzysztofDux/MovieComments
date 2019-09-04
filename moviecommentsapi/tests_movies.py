from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Movie, Rating
from .test_resources import camel_case_details, snake_case_details


class MovieModelTests(TestCase):

    def test_movie_create(self):
        """ Test if movie details are properly mapped """
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
        details_provider = MockMovieDetailsProvider()
        details = details_provider.get_details()
        movie = Movie.create("It", details_provider)
        try:
            r0 = self.create_rating_out_of_details(details, 0)
            r1 = self.create_rating_out_of_details(details, 1)
            r2 = self.create_rating_out_of_details(details, 2)
            self.assertIn(r0, movie.rating_set.all())
            self.assertIn(r1, movie.rating_set.all())
            self.assertIn(r2, movie.rating_set.all())
        except Rating.DoesNotExist:
            self.fail(msg="Rating for movie not created.")
        except Rating.MultipleObjectsReturned:
            self.fail(msg="Rating for movie created more than once.")

    @staticmethod
    def create_rating_out_of_details(details, index):
        return Rating.objects.get(source=details["Ratings"][index]["Source"],
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
        data = {'title': 'It'}
        expected_response = snake_case_details
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected_response)

    def test_response_after_another_movie_post(self):
        data = {'title': 'It'}
        expected_response = snake_case_details
        first_response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        another_response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(another_response .status_code, status.HTTP_200_OK)
        self.assertEqual(len(Movie.objects.all()), 1)
        self.assertEqual(another_response .data, expected_response)


class MockMovieDetailsProvider:
    def get_details(self):
        return camel_case_details
