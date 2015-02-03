from plone.dexterity.content import Container
from sllintra.content.content import Archive
from sllintra.content.interfaces import IArchive
from zope.interface.verify import verifyObject

import unittest


class ArchiveTestCase(unittest.TestCase):
    """TestCase for content type: sllintra.content.Archive"""

    def test_subclass(self):
        self.assertTrue(issubclass(Archive, Container))
        from sllintra.content.schema import ArchiveSchema
        self.assertTrue(issubclass(IArchive, ArchiveSchema))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IArchive, Archive()))
