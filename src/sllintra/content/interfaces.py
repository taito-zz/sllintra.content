from sllintra.content.schema import ArchiveSchema
from zope.interface import Interface


# Content type

class IArchive(ArchiveSchema):
    """Interface for content type: sllintra.content.Archive"""


# Behavior

class INameFromTitleOrFileName(Interface):
    """Marker interface to enable name from title or filename"""
