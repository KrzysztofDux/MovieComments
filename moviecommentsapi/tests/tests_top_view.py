import datetime
from itertools import zip_longest

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from .test_resources import get_saved_test_movie


class TopViewTests(APITestCase):
    maxDiff = None

    @staticmethod
    def get_url():
        return '/top/'

    @staticmethod
    def get_url_with_params(date_from, date_to):
        return f'/top/?from={date_from.strftime("%d %b %Y")}&to={date_to.strftime("%d %b %Y")}'

    @staticmethod
    def get_comment_with_date(movie, created_date):
        comment = movie.comments.create(text="test comment")
        comment.created_date = created_date
        comment.save()
        return comment

    def test_top_with_two_movies_no_comments_outside_range(self):
        """ Top should return ranking of movies by sum of their comments
        added in the provided date range. If all comments have created_date
        inside range, all should be taken into account. """
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        dates = [datetime.date(2019, 8, 5), datetime.date(2019, 8, 15), datetime.date(2019, 8, 20),
                 datetime.date(2019, 9, 1), datetime.date(2019, 9, 5)]
        for i, date in enumerate(dates):
            self.get_comment_with_date(movie if i % 2 == 0 else another_movie, date)
        expected = [{"MovieId": movie.pk, "TotalComments": 3, "Rank": 1},
                    {"MovieId": another_movie.pk, "TotalComments": 2, "Rank": 2}]
        ''' check for edge values '''
        self.check_result_for(dates[0], dates[-1], expected)
        ''' check for non-edge values '''
        self.check_result_for(dates[0] - datetime.timedelta(days=2),
                              dates[-1] + datetime.timedelta(days=2), expected)

    def test_top_with_two_movies_with_comments_outside_range(self):
        """ Top should return ranking of movies by sum of their comments
        added in the provided date range. If some comments have created_date
        outside range, they shouldn't be taken into account. """
        movie = get_saved_test_movie()
        second_movie = get_saved_test_movie()
        dates = [datetime.date(2019, 8, 5), datetime.date(2019, 8, 15), datetime.date(2019, 8, 20),
                 datetime.date(2019, 9, 1), datetime.date(2019, 9, 5)]
        for i, date in enumerate(dates):
            self.get_comment_with_date(movie if i % 2 == 0 else second_movie, date)

        ''' third movie outside of range shouldn't be included '''
        third_movie = get_saved_test_movie()
        self.get_comment_with_date(third_movie, dates[-1] + datetime.timedelta(days=+2))

        expected = [{"MovieId": second_movie.pk, "TotalComments": 2, "Rank": 1},
                    {"MovieId": movie.pk, "TotalComments": 1, "Rank": 2}]
        ''' check for edge values '''
        self.check_result_for(dates[1], dates[-2], expected)
        ''' check for non-edge values '''
        self.check_result_for(dates[1] - datetime.timedelta(days=2),
                              dates[-2] + datetime.timedelta(days=2), expected)

    def test_top_with_two_movies_no_comments_outside_range_rank_draw(self):
        """ Top should return ranking of movies by sum of their comments
        added in the provided date range. If in given date range both movies
        got the same number of comments, they should have the same rank. """
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        dates = [datetime.date(2019, 8, 5), datetime.date(2019, 8, 15), datetime.date(2019, 8, 20),
                 datetime.date(2019, 9, 1)]
        for i, date in enumerate(dates):
            self.get_comment_with_date(movie if i % 2 == 0 else another_movie, date)
        expected = [{"MovieId": movie.pk, "TotalComments": 2, "Rank": 1},
                    {"MovieId": another_movie.pk, "TotalComments": 2, "Rank": 1}]
        ''' check for edge values '''
        self.check_result_for(dates[0], dates[-1], expected)
        ''' check for non-edge values '''
        self.check_result_for(dates[0] - datetime.timedelta(days=2),
                              dates[-1] + datetime.timedelta(days=2), expected)

    def test_top_with_two_movies_with_comments_outside_range_rank_draw(self):
        """ Top should return ranking of movies by sum of their comments
        added in the provided date range. If in given date range both movies
        got the same number of comments, they should have the same rank. """
        movie = get_saved_test_movie()
        second_movie = get_saved_test_movie()
        dates = [datetime.date(2019, 8, 5), datetime.date(2019, 8, 15), datetime.date(2019, 8, 20),
                 datetime.date(2019, 9, 1), datetime.date(2019, 9, 5)]
        for i, date in enumerate(dates):
            self.get_comment_with_date(movie if i % 2 == 0 else second_movie, date)

        third_movie = get_saved_test_movie()
        self.get_comment_with_date(third_movie, dates[-2] - datetime.timedelta(days=2))

        expected = [{"MovieId": movie.pk, "TotalComments": 2, "Rank": 1},
                    {"MovieId": second_movie.pk, "TotalComments": 2, "Rank": 1},
                    {"MovieId": third_movie.pk, "TotalComments": 1, "Rank": 2}]
        ''' check for edge values '''
        self.check_result_for(dates[0], dates[-2], expected)
        ''' check for non-edge values '''
        self.check_result_for(dates[0] - datetime.timedelta(days=2),
                              dates[-2] + datetime.timedelta(days=2), expected)

    def test_top_with_include_all(self):
        """ If include_all flag is provided and set to True, films without comments
        in given range should also be included in ranking. """
        movie = get_saved_test_movie()
        second_movie = get_saved_test_movie()
        dates = [datetime.date(2019, 8, 5), datetime.date(2019, 8, 15), datetime.date(2019, 8, 20),
                 datetime.date(2019, 9, 1), datetime.date(2019, 9, 5)]
        for i, date in enumerate(dates):
            self.get_comment_with_date(movie if i % 2 == 0 else second_movie, date)

        third_movie = get_saved_test_movie()
        date_out_of_range = dates[-1] + datetime.timedelta(days=5)
        self.get_comment_with_date(third_movie, date_out_of_range)

        expected = [{"MovieId": second_movie.pk, "TotalComments": 2, "Rank": 1},
                    {"MovieId": movie.pk, "TotalComments": 1, "Rank": 2},
                    {"MovieId": third_movie.pk, "TotalComments": 0, "Rank": 3}]

        self.check_result_for(dates[1], dates[-2], expected, include_all=True)

    def check_result_for(self, date_from, date_to, expected, include_all=False):
        url = self.get_url_with_params(date_from, date_to)
        if include_all:
            url += "&include_all=True"
        response_on_edges = self.client.get(url, format='json')
        for rank, exp in zip_longest(json.loads(response_on_edges.content), expected):
            self.assertDictEqual(rank, exp)

    def test_top_for_call_without_date_range(self):
        """ Top should return ranking of movies only if date range is provided. """
        response = self.client.get(self.get_url(), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content).get("message"), "no date range provided")

    def test_top_for_call_without_one_date_boundary(self):
        """ Top should return ranking of movies only if date range is provided. """
        response = self.client.get(f"{self.get_url()}?from=06 Sep 2019", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content).get("message"), "no date range provided")

    def test_top_for_call_with_wrong_date_format(self):
        """ Top should return ranking of movies only if date range is provided. """
        response = self.client.get(f"{self.get_url()}?from=abc&to=123", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content).get("message"), "wrong date format provided")

    def test_top_for_call_with_one_param_empty(self):
        """ Top should return ranking of movies only if date range is provided. """
        response = self.client.get(f"{self.get_url()}?from=06 Sep 2019&to=", format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content).get("message"), "wrong date format provided")

