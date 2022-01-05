from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelations
from store.premissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationsSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelations__like=True, then=1))),
            rating=Avg('userbookrelations__rate')).select_related('owner').prefetch_related('readers').order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'id']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationsView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelations.objects.all()
    serializer_class = UserBookRelationsSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelations.objects.get_or_create(user=self.request.user,
                                                               book_id=self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'oauth.html')
