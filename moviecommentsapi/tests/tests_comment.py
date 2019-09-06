from django.test import TestCase
import datetime

from ..models import Comment
from .test_resources import get_saved_test_movie


class CommentTests(TestCase):

    def test_comments_for_movie_without_comments(self):
        movie = get_saved_test_movie()
        self.assertEqual(len(Comment.for_movie(movie)), 0)

    def test_comments_for_movie(self):
        movie = get_saved_test_movie()
        movie.comments.create(text="test comment 0")
        movie.comments.create(text="test comment 1")
        movie.comments.create(text="test comment 2")
        self.assertEqual(len(Comment.for_movie(movie)), 3)
        self.assertTrue(Comment.objects.get(text="test comment 0") in Comment.for_movie(movie))
        self.assertTrue(Comment.objects.get(text="test comment 1") in Comment.for_movie(movie))
        self.assertTrue(Comment.objects.get(text="test comment 2") in Comment.for_movie(movie))

    def test_calculate_comments_for_movie_in_date_range(self):
        movie = get_saved_test_movie()
        self.prepare_dates(movie)

        years_range = Comment.for_movie_in_range(movie, datetime.date(2016, 1, 1),
                                                 datetime.date(2018, 12, 30))
        self.assertEqual(len(years_range), 9)
        self.assertTrue(Comment.objects.get(text="test comment 1") in years_range)
        self.assertTrue(Comment.objects.get(text="test comment 4") in years_range)
        self.assertTrue(Comment.objects.get(text="test comment 8") in years_range)

        month_range = Comment.for_movie_in_range(movie, datetime.date(2016, 6, 1),
                                                 datetime.date(2016, 7, 31))

        self.assertTrue(Comment.objects.get(text="test comment 2") in month_range)
        self.assertTrue(Comment.objects.get(text="test comment 3") in month_range)
        self.assertEqual(len(month_range), 2)

        days_range = Comment.for_movie_in_range(movie, datetime.date(2018, 5, 5),
                                                datetime.date(2018, 5, 7))
        self.assertTrue(Comment.objects.get(text="test comment 6") in days_range)
        self.assertTrue(Comment.objects.get(text="test comment 7") in days_range)
        self.assertTrue(Comment.objects.get(text="test comment 8") in days_range)
        self.assertEqual(len(days_range), 3)

    @staticmethod
    def prepare_dates(movie):
        dates = [datetime.date(2015, 5, 4), datetime.date(2016, 5, 4), datetime.date(2016, 6, 4),
                 datetime.date(2016, 7, 4), datetime.date(2016, 8, 4), datetime.date(2018, 5, 4),
                 datetime.date(2018, 5, 5), datetime.date(2018, 5, 6), datetime.date(2018, 5, 7),
                 datetime.date(2018, 5, 8), datetime.date(2019, 5, 4)]
        for i, date in enumerate(dates):
            comment = movie.comments.create(text=f"test comment {i}")
            comment.created_date = date
            comment.save()