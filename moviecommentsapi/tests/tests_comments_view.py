import datetime

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from ..models import Comment
from .test_resources import get_saved_test_movie


class CommentsViewTests(APITestCase):
    maxDiff = None

    @staticmethod
    def get_url():
        return '/comments/'

    def test_comments_get(self):
        movie = get_saved_test_movie()
        movie.comments.create(text="test comment 1")
        movie.comments.create(text="test comment 2")
        movie.comments.create(text="test comment 3")
        now = datetime.date.today().strftime('%d %b %Y')

        expected = list()
        for i in range(1, 4):
            expected.append({"MovieId": movie.pk, "Text": f"test comment {i}", "CreatedDate": now})
        expected = sorted(expected, key=lambda k: k['Text'])

        response = self.client.get(self.get_url(), format='json')
        response_content = sorted(json.loads(response.content), key=lambda k: k['Text'])

        for resp, exp in zip(response_content, expected):
            self.assertDictEqual(resp, exp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comments_get_with_two_movies(self):
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        movie.comments.create(text="test comment 1")
        movie.comments.create(text="test comment 2")
        another_movie.comments.create(text="test comment for another movie 1")
        now = datetime.date.today().strftime('%d %b %Y')

        expected = list()
        for i in range(1, 3):
            expected.append({"MovieId": movie.pk, "Text": f"test comment {i}", "CreatedDate": now})
        expected.append({"MovieId": another_movie.pk, "Text": "test comment for another movie 1",
                          "CreatedDate": now})
        expected = sorted(expected, key=lambda k: k['Text'])

        response = self.client.get(self.get_url(), format='json')
        response_content = sorted(json.loads(response.content), key=lambda k: k['Text'])

        for resp, exp in zip(response_content, expected):
            self.assertDictEqual(resp, exp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comments_get_with_movie_id(self):
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        movie.comments.create(text="test comment 1")
        movie.comments.create(text="test comment 2")
        movie.comments.create(text="test comment 3")
        another_movie.comments.create(text="test comment for another movie 1")
        another_movie.comments.create(text="test comment for another movie 2")
        now = datetime.date.today().strftime('%d %b %Y')

        expected = list()
        for i in range(1, 3):
            expected.append(
                {"MovieId": another_movie.pk, "Text": f"test comment for another movie {i}",
                 "CreatedDate": now})
        expected = sorted(expected, key=lambda k: k['Text'])

        response = self.client.get(f"{self.get_url()}?Id={another_movie.pk}", format='json')
        response_content = sorted(json.loads(response.content), key=lambda k: k['Text'])

        for resp, exp in zip(response_content, expected):
            self.assertDictEqual(resp, exp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comments_get_movie_id_not_found(self):
        movie = get_saved_test_movie()
        response = self.client.get(f"{self.get_url()}?Id={movie.pk + 1}", format='json')
        self.assertEqual(json.loads(response.content).get("message"),
                         "movie with given id not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_comments_post(self):
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        data = {"Id": movie.pk, "Text": "test comment 1"}
        expected = {'MovieId': movie.pk, 'Text': 'test comment 1', 'CreatedDate': '06 Sep 2019'}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(json.loads(response.content), expected)
        self.assertEqual(len(Comment.for_movie(movie)), 1)
        self.assertEqual(Comment.for_movie(movie)[0].text, "test comment 1")
        self.assertEqual(len(Comment.for_movie(another_movie)), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comments_post_movie_id_not_found(self):
        movie = get_saved_test_movie()
        data = {"Id": movie.pk + 1, "Text": "test comment 1"}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(json.loads(response.content).get("message"),
                         "movie with given id not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
