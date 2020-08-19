from django.db import connection
from django.db.models.base import ModelBase
from django.test import TestCase
from django.db.utils import ProgrammingError

from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.abstract import TreeModel


class AbstractModelMixinTestCase(TestCase):
    """
    Base class for tests of model mixins/abstract models.
    To use, subclass and specify the mixin 'abstract_model' class variable.
    A model using the mixin will be made available in self.model
    """

    @classmethod
    def setUpClass(cls):
        # Create a dummy model which extends the mixin
        if not hasattr(cls, 'model'):
            cls.model = ModelBase(
                '__TestModel__' + cls.abstract_model.__name__,
                (cls.abstract_model,),
                {'__module__': cls.abstract_model.__module__}
            )

        # Create the schema for our test model. If the table already exists, will pass
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(cls.model)
            super().setUpClass()
        except ProgrammingError:
            pass

    @classmethod
    def tearDownClass(cls):
        # Delete the schema for the test model. If no table, will pass
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(cls.model)
            super().tearDownClass()
        except ProgrammingError:
            pass


class TestTreeModel(AbstractModelMixinTestCase):
    abstract_model = TreeModel

    def setUp(self):
        self.data = {
            "children": [
                {
                    "children": [
                        {
                            "children": [{}, {}, {}]
                        },
                        {
                            "children": [{}, {}, {}]
                        }
                    ]
                },
                {
                    "children": [
                        {},
                        {
                            "children": [{}, {}]
                        }
                    ]
                }
            ]
        }

    def test_load_tree(self):
        result_data = self.model._load_tree(self.data)
        expected_data = [
            ('1', 0, 2),
            ('1.1', 1, 2),
            ('1.1.1', 2, 3),
            ('1.1.1.1', 3, 0),
            ('1.1.1.2', 3, 0),
            ('1.1.1.3', 3, 0),
            ('1.1.2', 2, 3),
            ('1.1.2.1', 3, 0),
            ('1.1.2.2', 3, 0),
            ('1.1.2.3', 3, 0),
            ('1.2', 1, 2),
            ('1.2.1', 2, 0),
            ('1.2.2', 2, 2),
            ('1.2.2.1', 3, 0),
            ('1.2.2.2', 3, 0),
        ]
        self.assertEqual(expected_data, [(i.path, i.level, i.child_count) for i in result_data])

    def test_save_tree(self):
        root_elem = self.model.save_tree(self.data)

        self.assertEqual(root_elem.level, 0)
        self.assertEqual(root_elem.path, '1')
        self.assertEqual(self.model.objects.all().count(), 15)

        root_elem = self.model.save_tree(self.data)

        self.assertEqual(root_elem.level, 0)
        self.assertEqual(root_elem.path, '2')
        self.assertEqual(self.model.objects.all().count(), 30)

    def test_is_root(self):
        root_elem = self.model.save_tree(self.data)

        self.assertTrue(root_elem.is_root())
        self.assertFalse(self.model.objects.get(path='1.1').is_root())

    def test_is_leaf(self):
        root_elem = self.model.save_tree(self.data)

        self.assertTrue(self.model.objects.get(path='1.1.1.1').is_leaf())
        self.assertFalse(root_elem.is_leaf())

    def test_get_parents(self):
        self.model.save_tree(self.data)

        result_data = [i.path for i in self.model.objects.get(path='1.1.1.1').get_parents()]
        expected_data = ['1', '1.1', '1.1.1']

        self.assertEqual(result_data, expected_data)

    def test_get_children(self):
        root_elem = self.model.save_tree(self.data)

        result_data = [i.path for i in root_elem.get_children()]
        expected_data = ['1.1', '1.2']

        self.assertEqual(result_data, expected_data)

    def test_get_siblings(self):
        root_elem = self.model.save_tree(self.data)
        self.model.save_tree(self.data)

        result_data = [i.path for i in root_elem.get_siblings()]
        expected_data = ['2']

        self.assertEqual(result_data, expected_data)

        result_data = [i.path for i in self.model.objects.get(path='1.1.1').get_siblings()]
        expected_data = ['1.1.2']

        self.assertEqual(result_data, expected_data)

        result_data = [i.path for i in self.model.objects.get(path='1.1.1.1').get_siblings()]
        expected_data = ['1.1.1.2', '1.1.1.3']

        self.assertEqual(result_data, expected_data)


class CategoryAPITest(APITestCase):
    def setUp(self):
        self.data = {
            "name": "Category 1",
            "children": [
                {
                    "name": "Category 1.1",
                    "children": [
                        {
                            "name": "Category 1.1.1",
                            "children": [
                                {
                                    "name": "Category 1.1.1.1"
                                },
                                {
                                    "name": "Category 1.1.1.2"
                                },
                                {
                                    "name": "Category 1.1.1.3"
                                }
                            ]
                        },
                        {
                            "name": "Category 1.1.2",
                            "children": [
                                {
                                    "name": "Category 1.1.2.1"
                                },
                                {
                                    "name": "Category 1.1.2.2"
                                },
                                {
                                    "name": "Category 1.1.2.3"
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Category 1.2",
                    "children": [
                        {
                            "name": "Category 1.2.1"
                        },
                        {
                            "name": "Category 1.2.2",
                            "children": [
                                {
                                    "name": "Category 1.2.2.1"
                                },
                                {
                                    "name": "Category 1.2.2.2"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def test_api(self):
        response = self.client.post('/categories/', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        root_id = response.data['id']
        second_child_id = response.data['children'][0]['id']

        response = self.client.get(f'/categories/{root_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/categories/{second_child_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_required_fields_errors(self):
        error_data = {
            "name": "",
            "children": [
                {
                    "name": ""
                }
            ]
        }

        response = self.client.post('/categories/', data=error_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue('name' in response.data)
        self.assertTrue('name' in response.data['children'][0])

    def test_unique_name_errors(self):
        error_data = {
            "name": "Category 1",
            "children": [
                {
                    "name": "Category 1",
                    "children": [
                        {
                            "name": "Category 1.1.1",
                            "children": [
                                {
                                    "name": "Category 1.1.1.1"
                                },
                                {
                                    "name": "Category 1.1.1.1"
                                }
                            ]
                        }, {
                            "name": "Category 1.1.1",
                        }
                    ]
                }
            ]
        }

        response = self.client.post('/categories/', data=error_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue('name' in response.data['children'][0])
        self.assertTrue('name' in response.data['children'][0]['children'][1])
        self.assertTrue('name' in response.data['children'][0]['children'][0]['children'][1])

        response = self.client.post('/categories/', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/categories/', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue('name' in response.data)

    def test_empty_data_errors(self):
        response = self.client.post('/categories/', data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue('name' in response.data)

