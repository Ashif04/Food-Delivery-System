import unittest

import app.models
from app.db.base import Base
from sqlalchemy.orm import configure_mappers


class ModelRegistryTests(unittest.TestCase):
    def test_all_models_register_and_configure(self) -> None:
        configure_mappers()
        self.assertEqual(len(Base.metadata.tables), 34)
