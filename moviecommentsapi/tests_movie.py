from django.test import TestCase
from .models import Movie, Rating
from .test_resources import MockMovieDetailsProvider


class MovieModelTests(TestCase):

    def test_movie_create(self):
        """ Testing if movie details are properly mapped. """
        details_provider = MockMovieDetailsProvider()
        details = details_provider.get_details(None)
        movie_attrs = ["title", "year", "rated", "released", "runtime", "genre", "director",
                       "writer", "actors", "plot", "language", "country", "awards", "poster",
                       "metascore", "imdb_rating", "imdb_votes", "imdb_id", "type", "dvd",
                       "box_office", "production", "website"]
        details_attr = ["Title", "Year", "Rated", "Released", "Runtime", "Genre", "Director",
                        "Writer", "Actors", "Plot", "Language", "Country", "Awards", "Poster",
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
        details = details_provider.get_details(None)
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
        return Rating.objects.get(source=details["Ratings"][index]["Source"],
                                  value=details["Ratings"][index]["Value"])
