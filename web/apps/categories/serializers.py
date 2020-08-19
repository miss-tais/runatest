from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from apps.categories import models
from apps.categories.exceptions import TreePathMaxLengthException
from apps.categories.fields import RecursiveField


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'name')


class CategoryCreateSerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(child=RecursiveField(), required=False)

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'children')
        extra_kwargs = {
            "name": {
                "validators": [],
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'unique_names' not in self.context:
            self.context['unique_names'] = list(models.Category.objects.all().values_list('name', flat=True))

    def validate_name(self, value):
        if value in self.context['unique_names']:
            raise serializers.ValidationError(_(f'{self.Meta.model.__name__} with this name already exists.'), code='unique')

        self.context['unique_names'].append(value)
        return value

    def save(self, **kwargs):
        try:
            self.instance = self.Meta.model.save_tree(self.validated_data)
        except TreePathMaxLengthException as e:
            raise serializers.ValidationError(e)
        return self.instance


class CategoryReadSerializer(serializers.ModelSerializer):
    children = CategorySerializer(many=True)
    parents = CategorySerializer(many=True)
    siblings = CategorySerializer(many=True)

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'children', 'parents', 'siblings')
        read_only_fields = fields
