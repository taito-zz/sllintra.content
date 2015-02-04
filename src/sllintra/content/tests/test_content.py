from plone.dexterity.content import Container
from sllintra.content.content import Archive
from sllintra.content.interfaces import IArchive
from zope.interface.verify import verifyObject
from sllintra.content.schema import ArchiveSchema

import unittest


class ArchiveTestCase(unittest.TestCase):
    """TestCase for content type: sllintra.content.Archive"""

    def test_subclass(self):
        from plone.app.dexterity.behaviors.metadata import IBasic
        self.assertTrue(issubclass(Archive, Container))
        self.assertTrue(issubclass(ArchiveSchema, IBasic))
        self.assertTrue(issubclass(IArchive, ArchiveSchema))

    def test_verifyObject(self):
        self.assertTrue(verifyObject(IArchive, Archive()))

    def test_schema__title(self):
        attr = ArchiveSchema.get('title')
        self.assertFalse(attr.required)

    def test_schema__archive_file(self):
        attr = ArchiveSchema.get('archive_file')
        from plone.namedfile.field import NamedBlobFile
        self.assertTrue(isinstance(attr, NamedBlobFile))
        self.assertEqual(attr.title, u'Archive File')
        self.assertFalse(attr.required)

    def test_content(self):
        content = Archive()
        self.assertIsNone(content.archive_file)
