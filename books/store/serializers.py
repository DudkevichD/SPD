from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelations

class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class BookSerializer(ModelSerializer):
    # likes_count = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner = serializers.CharField(source='owner.username', default='', read_only=True)
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'annotated_likes', 'rating', 'owner', 'readers')

    # def get_likes_count(self, instance):
    #     return UserBookRelations.objects.filter(book=instance, like=True).count()


class UserBookRelationsSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelations
        fields = ('book', 'like', 'in_bookmarks', 'rate')
