from plone.app.dexterity.behaviors.metadata import IBasic
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContainer
from sllintra.content.schema import ArchiveSchema
from zope.interface import Interface
from zope.interface import alsoProvides


# Content type

class IArchive(ArchiveSchema, IDexterityContainer):
    """Interface for content type: sllintra.content.Archive"""


# Behavior

class INameFromTitleOrFileName(Interface):
    """Marker interface to enable name from title or filename"""


class IBasic(IBasic):
    """Override plone.app.dexterity.behaviors.metadata.IBasic to make title unrequisite"""


IBasic.get('title').required = False


alsoProvides(IBasic, IFormFieldProvider)
