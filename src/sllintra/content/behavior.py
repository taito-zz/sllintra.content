from Products.CMFPlone.utils import safe_hasattr
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity.behaviors.filename import NameFromFileName
from plone.dexterity.utils import iterSchemata
from plone.namedfile.field import NamedBlobFile
from sllintra.content.interfaces import INameFromTitleOrFileName
from zope.component import adapts
from zope.interface import implements
from zope.schema import getFieldsInOrder


class NameFromTitleOrFileName(NameFromFileName):
    implements(INameFromTitle)
    adapts(INameFromTitleOrFileName)

    def __new__(cls, context):
        instance = super(NameFromFileName, cls).__new__(cls)

        if safe_hasattr(context, 'title') and not context.title:

            file_field = None
            for i in iterSchemata(context):
                fields = getFieldsInOrder(i)
                for name, field in fields:
                    if isinstance(field, NamedBlobFile):
                        file_field = field
                        break
            if file_field is None:
                return None
            filename = getattr(file_field.get(context), 'filename', None)
            if not isinstance(filename, basestring) or not filename:
                return None

            title = filename
            context.title = title

        else:
            instance = super(NameFromFileName, cls).__new__(cls)
            title = context.title

        instance.title = title
        return instance
