import datetime

from rest_framework.test import APITestCase
from rest_framework.utils import json

from .test_resources import get_saved_test_movie


class CommentsViewTests(APITestCase):
    maxDiff = None

    @staticmethod
    def get_url():
        return '/comments/'

    def test_comments(self):
        movie = get_saved_test_movie()
        movie.comments.create(text="test comment 1")
        movie.comments.create(text="test comment 2")
        movie.comments.create(text="test comment 3")
        response = self.client.get(self.get_url(), format='json')
        now = datetime.date.today().strftime('%d %b %Y')
        expected = list()
        for i in range(1, 4):
            expected.append({"MovieId": movie.pk, "Text": f"test comment {i}", "CreatedDate": now})
        self.assertEqual(json.loads(response.content), expected)

    def test_comments_with_movie_id(self):
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        movie.comments.create(text="test comment 1")
        movie.comments.create(text="test comment 2")
        movie.comments.create(text="test comment 3")
        another_movie.comments.create(text="comment for another movie 1")
        another_movie.comments.create(text="comment for another movie 2")
        response = self.client.get(f"{self.get_url()}?Id={another_movie.pk}", format='json')
        now = datetime.date.today().strftime('%d %b %Y')
        expected = list()
        for i in range(1, 3):
            expected.append(
                {"MovieId": another_movie.pk, "Text": f"comment for another movie {i}", "CreatedDate": now})
        self.assertEqual(json.loads(response.content), expected)
