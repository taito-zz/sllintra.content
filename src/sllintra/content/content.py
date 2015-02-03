from plone.dexterity.content import Container
from sllintra.content.interfaces import IArchive
from zope.interface import implements


class Archive(Container):
    """Content type: sllintra.content.Archive"""
    implements(IArchive)
