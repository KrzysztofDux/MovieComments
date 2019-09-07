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
        """ GET request should return all saved comments. """
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
        """ GET request should return all saved comments. """
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
        """ GET request with id param should return all comments regarding
        movie with provided id. """
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

        response = self.client.get(f"{self.get_url()}?id={another_movie.pk}", format='json')
        response_content = sorted(json.loads(response.content), key=lambda k: k['Text'])

        for resp, exp in zip(response_content, expected):
            self.assertDictEqual(resp, exp)
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comments_get_with_wrong_movie_id(self):
        """ If id provided as param is formatted incorrectly
        information about it should be returned. """
        response = self.client.get(f'{self.get_url()}?id="abc"', format='json')
        self.assertEqual(json.loads(response.content).get("message"), "wrong id provided")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comments_get_movie_id_not_found(self):
        """ If id provided as param doesn't point to any saved movie
        information about it should be returned. """
        movie = get_saved_test_movie()
        response = self.client.get(f"{self.get_url()}?id={movie.pk + 1}", format='json')
        self.assertEqual(json.loads(response.content).get("message"),
                         "movie with given id not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_comments_post(self):
        """ If correct movie id and text are provided in POST request new
        comment should be created and attached to movie with given id. """
        movie = get_saved_test_movie()
        another_movie = get_saved_test_movie()
        data = {"id": movie.pk, "text": "test comment 1"}
        expected = {'MovieId': movie.pk, 'Text': 'test comment 1',
                    'CreatedDate': datetime.date.today().strftime('%d %b %Y')}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(json.loads(response.content), expected)
        self.assertEqual(len(Comment.for_movie(movie)), 1)
        self.assertEqual(Comment.for_movie(movie)[0].text, "test comment 1")
        self.assertEqual(len(Comment.for_movie(another_movie)), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comments_post_movie_id_not_found(self):
        """ If id provided as param doesn't point to any saved movie
        information about it should be returned. """
        movie = get_saved_test_movie()
        data = {"id": movie.pk + 1, "text": "test comment 1"}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(json.loads(response.content).get("message"),
                         "movie with given id not found")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_comments_post_movie_wrong_id(self):
        """ If id provided as param is formatted incorrectly
        information about it should be returned. """
        data = {"id": "abc", "text": "test comment 1"}
        response = self.client.post(self.get_url(), data, format='json')
        self.assertEqual(json.loads(response.content).get("message"), "wrong id provided")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
