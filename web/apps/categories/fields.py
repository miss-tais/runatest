from rest_framework import serializers, fields


class RecursiveField(serializers.Field):
    """Recursive field for tree structure"""

    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs
        self._child = None

        super().__init__(*args, **kwargs)

    @property
    def child(self):
        if not self._child:
            self._child = self.parent.parent.__class__(context=self.parent.parent.context, **self.init_kwargs)
        return self._child

    def to_representation(self, value):
        return self.child.to_representation(value)

    def run_validation(self, data=fields.empty):
        return self.child.run_validation(data)
