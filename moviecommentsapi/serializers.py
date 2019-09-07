from django.db import transaction
from rest_framework import serializers
from .models import Movie, Rating, Comment, short, medium, long


class CommentSerializer(serializers.Serializer):
    MovieId = serializers.PrimaryKeyRelatedField(many=False, queryset=Movie.objects.all(),
                                                 source="movie", required=False)
    Text = serializers.CharField(max_length=long, source="text")
    CreatedDate = serializers.DateField(format='%d %b %Y', input_formats=['iso-8601', '%d %b %Y'],
                                        source="created_date")

    class Meta:
        model = Comment
        fields = ("movie", "text", "created_date")

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        if "created_date" in validated_data.keys():
            comment.created_date = validated_data["created_date"]
        comment.save()
        return comment

    def update(self, instance, validated_data):
        pass


class RatingSerializer(serializers.Serializer):
    Source = serializers.CharField(max_length=medium, source="source")
    Value = serializers.CharField(max_length=short, source="value")

    class Meta:
        model = Rating
        fields = ("source", "value")

    def create(self, validated_data):
        return Rating.objects.create(**validated_data)

    def update(self, instance, validated_data):
        pass


class MovieSerializer(serializers.Serializer):
    Id = serializers.IntegerField(required=False, read_only=True, source="pk")
    Title = serializers.CharField(max_length=long, source="title")
    Year = serializers.CharField(max_length=short, source="year")
    Rated = serializers.CharField(max_length=short, source="rated")
    Released = serializers.CharField(max_length=medium, source="released")
    Runtime = serializers.CharField(max_length=medium, source="runtime")
    Genre = serializers.CharField(max_length=medium, source="genre")
    Director = serializers.CharField(max_length=long, source="director")
    Writer = serializers.CharField(max_length=long, source="writer")
    Actors = serializers.CharField(max_length=long, source="actors")
    Plot = serializers.CharField(max_length=long, source="plot")
    Language = serializers.CharField(max_length=medium, source="language")
    Country = serializers.CharField(max_length=medium, source="country")
    Awards = serializers.CharField(max_length=medium, source="awards")
    Poster = serializers.CharField(max_length=long, source="poster")
    Ratings = RatingSerializer(many=True, required=False, source="ratings")
    Metascore = serializers.CharField(max_length=short, source="metascore")
    imdbRating = serializers.CharField(max_length=short, source="imdb_rating")
    imdbVotes = serializers.CharField(max_length=medium, source="imdb_votes")
    imdbID = serializers.CharField(max_length=medium, source="imdb_id")
    Type = serializers.CharField(max_length=medium, source="type")
    DVD = serializers.CharField(max_length=medium, source="dvd")
    BoxOffice = serializers.CharField(max_length=medium, source="box_office")
    Production = serializers.CharField(max_length=medium, source="production")
    Website = serializers.CharField(max_length=long, source="website")

    class Meta:
        model = Movie
        fields = ("pk", "title", "year", "rated", "released", "runtime", "genre", "director",
                  "writer", "actors", "plot", "language", "country", "awards", "poster", "ratings",
                  "metascore", "imdb_rating", "imdb_votes", "imdb_id", "type", "dvd",
                  "box_office", "production", "website")

    def create(self, validated_data):
        if "pk" in validated_data.keys():
            validated_data['pk'] = str(validated_data['year'])
        validated_data['year'] = int(validated_data['year'])
        validated_data['metascore'] = int(validated_data['metascore'])
        validated_data['imdb_rating'] = float(validated_data['imdb_rating'])
        with transaction.atomic():
            ratings_data = validated_data.pop("ratings")
            movie = Movie.objects.create(**validated_data)
            for rd in ratings_data:
                movie.ratings.create(source=rd["source"], value=rd["value"])
        return movie

    def update(self, instance, validated_data):
        pass
