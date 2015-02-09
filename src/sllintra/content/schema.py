from plone.app.dexterity.behaviors.metadata import IBasic
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from sllintra.content import _


class ArchiveSchema(IBasic):
    """Schema for content type: sllintra.content.Archive"""

    model.primary('archive_file')
    archive_file = NamedBlobFile(
        title=_(u'Archive File'),
        required=False)


ArchiveSchema.get('title').required = False
