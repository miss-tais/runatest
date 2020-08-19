from rest_framework import mixins, viewsets

from apps.categories import serializers
from apps.categories import models


class CategoriesView(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):

    queryset = models.Category.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CategoryCreateSerializer
        return serializers.CategoryReadSerializer
