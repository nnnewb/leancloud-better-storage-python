from unittest import TestCase

from leancloud_better_storage.storage import models, fields


class TestDeclaration(TestCase):

    def test_declare_model(self):
        class Person(models.Model):
            name = fields.Field()

        self.assertIn('name', Person.__fields__)

    def test_declare_inherit_model(self):
        class BaseModel(models.Model):
            name = fields.Field()

        class Person(BaseModel):
            age = fields.Field()

        self.assertIn('name', Person.__fields__)
        self.assertIn('age', Person.__fields__)

    def test_declare_multiple_inherit_model(self):
        class BaseModelA(models.Model):
            name = fields.Field()

        class BaseModelB(models.Model):
            age = fields.Field()

        class PersonA(BaseModelA, BaseModelB):
            pass

        class PersonB(BaseModelA, BaseModelB):
            bio = fields.Field()

        self.assertIn('name', PersonA.__fields__)
        self.assertIn('age', PersonA.__fields__)
        self.assertIn('name', PersonB.__fields__)
        self.assertIn('age', PersonB.__fields__)
        self.assertIn('bio', PersonB.__fields__)

