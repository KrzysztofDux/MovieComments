import abc

from django.db import models

# CharField max_lengths

short, medium, long = 30, 300, 600


class Movie(models.Model):

    @classmethod
    def create(cls, title, details_provider):
        if not isinstance(details_provider, Movie.AbstractDetailsProvider):
            raise TypeError("details_provider must implement Movie.AbstractDetailsProvider.")
        return cls.__create_movie_with_details_from_provider(title, details_provider)

    @staticmethod
    def __create_movie_with_details_from_provider(title, details_provider):
        details = details_provider.get_details(title)
        formal_title = details_provider.get_formal_title(title)
        if Movie.objects.filter(title=formal_title).exists():
            raise Movie.DuplicateError
        serializer = details_provider.get_serializer(data=details)
        serializer.is_valid(True)
        return serializer.save()

    title = models.CharField(max_length=long)
    year = models.IntegerField()
    rated = models.CharField(max_length=short)
    released = models.CharField(max_length=medium)
    runtime = models.CharField(max_length=medium)
    genre = models.CharField(max_length=medium)
    director = models.CharField(max_length=long)
    writer = models.CharField(max_length=long)
    actors = models.CharField(max_length=long)
    plot = models.CharField(max_length=long)
    language = models.CharField(max_length=medium)
    country = models.CharField(max_length=medium)
    awards = models.CharField(max_length=long)
    poster = models.CharField(max_length=long)
    metascore = models.CharField(max_length=short)
    imdb_rating = models.CharField(max_length=short)
    imdb_votes = models.CharField(max_length=medium)
    imdb_id = models.CharField(max_length=medium)
    type = models.CharField(max_length=medium)
    dvd = models.CharField(max_length=medium)
    box_office = models.CharField(max_length=medium)
    production = models.CharField(max_length=medium)
    website = models.CharField(max_length=long)

    class DuplicateError(Exception):
        """ Movie already exists in database. Uniqueness ensured
        this way to greatly reduce complexity of testing. """
        pass

    class AbstractDetailsProvider(metaclass=abc.ABCMeta):
        def get_details(self, title):
            pass

        def get_formal_title(self, title):
            pass

        def get_serializer(self, **kwargs):
            pass


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    source = models.CharField(max_length=50)
    value = models.CharField(max_length=10)


class Comment(models.Model):

    @staticmethod
    def for_movie(movie):
        return list(Comment.objects.filter(movie=movie))

    @staticmethod
    def for_movie_in_range(movie, date_from, date_to):
        return list(Comment.objects.filter(movie=movie, created_date__gte=date_from,
                                           created_date__lte=date_to))

    @staticmethod
    def sum_for_movie_in_range(movie, date_from, date_to):
        return Comment.objects.filter(movie=movie, created_date__gte=date_from,
                                      created_date__lte=date_to).count()

    @staticmethod
    def in_range(date_from, date_to):
        return list(Comment.objects.filter(created_date__gte=date_from, created_date__lte=date_to))

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    created_date = models.DateField(auto_now_add=True)
    text = models.TextField()
