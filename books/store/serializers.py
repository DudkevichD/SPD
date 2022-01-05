from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelations


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class UserBookRelationsSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelations
        fields = ('book', 'like', 'in_bookmarks', 'rate')

