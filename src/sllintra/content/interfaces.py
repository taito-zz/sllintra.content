from plone.app.dexterity.behaviors.metadata import IBasic
from plone.autoform.interfaces import IFormFieldProvider
from sllintra.content.schema import ArchiveSchema
from zope.interface import Interface
from zope.interface import alsoProvides


# Content type

class IArchive(ArchiveSchema):
    """Interface for content type: sllintra.content.Archive"""


# Behavior

class INameFromTitleOrFileName(Interface):
    """Marker interface to enable name from title or filename"""


class IBasic(IBasic):
    """Behavior interface to provide non-required title and description field"""


IBasic.get('title').required = False


alsoProvides(IBasic, IFormFieldProvider)
