from django.db import models

# CharField max_lengths
short, medium, long = 10, 50, 300


class Movie(models.Model):
    default_details_provider = None

    @classmethod
    def create(cls, title, details_provider=default_details_provider):
        try:
            return cls.__create_movie_with_details_from_provider(title, details_provider)
        except AttributeError:
            raise ValueError("details_provider must provide get_details(str) method")

    @staticmethod
    def __create_movie_with_details_from_provider(title, details_provider):
        from .serializers import MovieSerializer
        details = details_provider.get_details(title)
        serializer = MovieSerializer(data=details)
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
    awards = models.CharField(max_length=medium)
    poster = models.CharField(max_length=long)
    metascore = models.IntegerField()
    imdb_rating = models.DecimalField(decimal_places=1, max_digits=4)
    imdb_votes = models.IntegerField()
    imdb_id = models.CharField(max_length=medium)
    type = models.CharField(max_length=medium)
    dvd = models.CharField(max_length=medium)
    box_office = models.CharField(max_length=medium)
    production = models.CharField(max_length=medium)
    website = models.CharField(max_length=long)


class Rating(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    source = models.CharField(max_length=medium)
    value = models.CharField(max_length=short)


class Comment(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    text = models.TextField()
