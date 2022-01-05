import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelations
from store.serializers import BookSerializer


class BoolSerializerTestCase(TestCase):
    def test_ok(self):
        user_1 = User.objects.create(username='User_1', first_name='DI', last_name='DU')
        user_2 = User.objects.create(username='User_2', first_name='MA', last_name='KA')
        user_3 = User.objects.create(username='User_3', first_name='CO', last_name='KO')

        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author')
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author')

        UserBookRelations.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelations.objects.create(user=user_2, book=book_1, like=True, rate=5)
        UserBookRelations.objects.create(user=user_3, book=book_1, like=True, rate=5)

        UserBookRelations.objects.create(user=user_1, book=book_2, like=False, rate=3)
        UserBookRelations.objects.create(user=user_2, book=book_2, like=False, rate=3)
        UserBookRelations.objects.create(user=user_3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            rating=Avg('userbookrelations__rate')).order_by('id')

        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author',
                'annotated_likes': 3,
                'rating': '5.00',
                "owner": "",
                'readers': [
                    {
                        'first_name': 'DI',
                        'last_name': 'DU'
                    },
                    {
                        'first_name': 'MA',
                        'last_name': 'KA'
                    },
                    {
                        'first_name': 'CO',
                        'last_name': 'KO'
                    },
                ]

            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author',
                'annotated_likes': 0,
                'rating': '3.00',
                "owner": "",
                'readers': [
                    {
                        'first_name': 'DI',
                        'last_name': 'DU'
                    },
                    {
                        'first_name': 'MA',
                        'last_name': 'KA'
                    },
                    {
                        'first_name': 'CO',
                        'last_name': 'KO'
                    },
                ]
            }
        ]
        # print()
        # for i in data:
        #     print(json.dumps(i))
        #
        # print()
        # for i in expected_data:
        #     print(i)
        # # print(json.dumps(data))
        # # print()
        # # print(expected_data)

        self.assertEqual(data, expected_data)
