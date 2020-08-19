from django.db import models


class TreeManager(models.Manager):
    """Manager for tree model."""

    def get_queryset(self):
        return super().get_queryset().order_by('path')
