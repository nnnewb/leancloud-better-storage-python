from unittest import TestCase

from leancloud_better_storage.storage import models
from leancloud_better_storage.storage.fields import Field


class TestDeclaration(TestCase):

    def test_declare_model(self):
        class Person(models.Model):
            name = Field()

        self.assertIn('name', Person.__fields__)

    def test_declare_inherit_model(self):
        class BaseModel(models.Model):
            name = Field()

        class Person(BaseModel):
            age = Field()

        self.assertIn('name', Person.__fields__)
        self.assertIn('age', Person.__fields__)

    def test_declare_multiple_inherit_model(self):
        class BaseModelA(models.Model):
            name = Field()

        class BaseModelB(models.Model):
            age = Field()

        class PersonA(BaseModelA, BaseModelB):
            pass

        class PersonB(BaseModelA, BaseModelB):
            bio = Field()

        self.assertIn('name', PersonA.__fields__)
        self.assertIn('age', PersonA.__fields__)
        self.assertIn('name', PersonB.__fields__)
        self.assertIn('age', PersonB.__fields__)
        self.assertIn('bio', PersonB.__fields__)

