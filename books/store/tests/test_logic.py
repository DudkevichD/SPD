from django.contrib.auth.models import User
from django.test import TestCase
from store.logic import set_rating
from store.models import Book, UserBookRelations


class SetRatingTestCase(TestCase):
    def setUp(self):
        user_1 = User.objects.create(username='User_1', first_name='DI', last_name='DU')
        user_2 = User.objects.create(username='User_2', first_name='MA', last_name='KA')
        user_3 = User.objects.create(username='User_3', first_name='CO', last_name='KO')

        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author', owner=user_1)

        UserBookRelations.objects.create(user=user_1, book=self.book_1, like=False, rate=3)
        UserBookRelations.objects.create(user=user_2, book=self.book_1, like=False, rate=4)
        UserBookRelations.objects.create(user=user_3, book=self.book_1, like=False, rate=4)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(str(self.book_1.rating), '3.67')
