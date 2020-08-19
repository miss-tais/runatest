import collections

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.categories.managers import TreeManager
from apps.categories.exceptions import TreePathMaxLengthException


class TreeModel(models.Model):
    """
    Base class for tree models.
    """

    path = models.CharField(
        db_index=True,
        unique=True,
        max_length=255,
        verbose_name=_('path')
    )

    level = models.PositiveIntegerField(
        db_index=True,
        verbose_name=_("level")
    )

    child_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("child count")
    )

    objects = TreeManager()

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.path}"

    @classmethod
    def _load_tree(cls, tree_data=None):
        items = []

        if tree_data is not None:
            max_length = cls._meta.get_field('path').max_length
            tree_id = cls.objects.exclude(path__contains='.').count() + 1

            Child = collections.namedtuple('Child', 'parent data order level')
            children = [Child(parent=None, data=tree_data.copy(), order=None, level=0)]

            while children:
                item = children.pop()

                new_children = item.data.pop('children', [])

                path = f"{item.parent.path}.{item.order}" if item.parent else f"{tree_id}"

                if len(path) > max_length:
                    raise TreePathMaxLengthException(_('One of the children is too deep in the tree, '
                                                       'try increasing the path.max_length property'))

                obj = cls(path=path, level=item.level, child_count=len(new_children), **item.data)

                items.append(obj)

                if new_children:
                    new_children = [
                        Child(parent=obj, data=i.copy(), order=index + 1, level=item.level + 1)
                        for index, i in enumerate(new_children)
                    ]
                    new_children.reverse()

                    children.extend(new_children)

        return items

    @classmethod
    def save_tree(cls, tree_data=None):
        if tree_data is not None:
            return cls.objects.bulk_create(cls._load_tree(tree_data))[0]

    def is_leaf(self):
        return self.child_count == 0

    def is_root(self):
        return self.level == 0

    def get_parents(self):
        if self.is_root():
            return self.__class__.objects.none()

        parent_paths = self.path.split('.')[:-1]
        parent_paths = ['.'.join(parent_paths[:i + 1]) for i in range(len(parent_paths))]

        return self.__class__.objects.filter(path__in=parent_paths)

    def get_siblings(self, include_self=False):
        queryset = self.__class__.objects.filter(level=self.level)

        if not self.is_root():
            base_path = ".".join(self.path.split('.')[:-1])
            queryset = queryset.filter(path__startswith=base_path)

        if not include_self:
            queryset = queryset.exclude(pk=self.pk)

        return queryset

    def get_children(self):
        if self.is_leaf():
            return self.__class__.objects.none()

        return self.__class__.objects.filter(level=self.level + 1, path__startswith=self.path)

    @property
    def parents(self):
        return self.get_parents()

    @property
    def siblings(self):
        return self.get_siblings()

    @property
    def children(self):
        return self.get_children()
