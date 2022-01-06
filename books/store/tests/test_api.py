import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelations
from store.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name='Test book 1',
                                          price=25,
                                          author_name='Author_1',
                                          owner=self.user
                                          )
        self.book_2 = Book.objects.create(name='Test book 2',
                                          price=55,
                                          author_name='Author 1',
                                          owner=self.user
                                          )
        self.book_3 = Book.objects.create(name='Test book 3 Author_1',
                                          price=55,
                                          author_name='Author 2',
                                          owner=self.user
                                          )

    def test_qet(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1)))).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1)))).order_by('id')
        response = self.client.get(url, data={'price': '55.00'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1)))).order_by('id')
        response = self.client.get(url, data={'search': 'Author_1'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Book 2",
            "price": "52.00",
            "author_name": "author"
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_user2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(response.data, {
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')})
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_user2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())


class BookRelationsApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='test_user_1')
        self.user_2 = User.objects.create(username='test_user_2')
        self.book_1 = Book.objects.create(name='Test book 1',
                                          price=25,
                                          author_name='Author_1',
                                          owner=self.user_1
                                          )
        self.book_2 = Book.objects.create(name='Test book 2',
                                          price=55,
                                          author_name='Author 1',
                                          owner=self.user_2
                                          )

    def test_like(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelations.objects.get(user=self.user_1, book=self.book_1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelations.objects.get(user=self.user_1, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelations.objects.get(user=self.user_1, book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wronge(self):
        url = reverse('userbookrelations-detail', args=(self.book_1.id,))
        data = {
            "rate": 6,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
