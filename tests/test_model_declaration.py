from unittest import TestCase
from leancloud_better_storage.storage import models, fields


class TestModelDeclaration(TestCase):

    def test_declare_model(self):
        class MyModel(models.Model):
            name = fields.Field()

        self.assertIn('name', MyModel.__fields__)

    def test_declare_inherit_model(self):
        class BaseModel(models.Model):
            name = fields.Field()

        class MyModel(BaseModel):
            age = fields.Field()

        self.assertIn('name', MyModel.__fields__)
        self.assertIn('age', MyModel.__fields__)

    def test_declare_multiple_inherit_model(self):
        class BaseModelA(models.Model):
            name = fields.Field()

        class BaseModelB(models.Model):
            age = fields.Field()

        class ModelA(BaseModelA, BaseModelB):
            pass

        class ModelB(BaseModelA, BaseModelB):
            bio = fields.Field()

        self.assertIn('name', ModelA.__fields__)
        self.assertIn('age', ModelA.__fields__)
        self.assertIn('name', ModelB.__fields__)
        self.assertIn('age', ModelB.__fields__)
        self.assertIn('bio', ModelB.__fields__)
