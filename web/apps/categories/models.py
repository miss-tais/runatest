from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.categories.abstract import TreeModel


class Category(TreeModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name")
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return f'{self.name}'

