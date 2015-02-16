from plone.dexterity.interfaces import IDexterityContainer
from plone.supermodel.model import Schema
from sllintra.content.interfaces import IArchive
from sllintra.content.schema import ArchiveSchema

import unittest


class ArchiveTestCase(unittest.TestCase):
    """TestCase for IArchive interface"""

    def test_subclass(self):
        self.assertTrue(issubclass(ArchiveSchema, Schema))
        self.assertTrue(issubclass(IArchive, (ArchiveSchema, IDexterityContainer)))
