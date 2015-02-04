from plone.app.dexterity.behaviors.metadata import IBasic
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from sllintra.content import _
from zope.interface import Invalid
from zope.interface import invariant


class FileTitleInvalid(Invalid):
    __doc__ = _(u'Add archive file or title.')


class ArchiveSchema(IBasic):
    """Schema for content type: sllintra.content.Archive"""

    model.primary('archive_file')
    archive_file = NamedBlobFile(
        title=_(u'Archive File'),
        required=False)

    @invariant
    def validateTitleArchiveFile(data):
        if data.title is None and data.archive_file is None:
            raise FileTitleInvalid(_(u'Add archive file or title.'))


ArchiveSchema.get('title').required = False
