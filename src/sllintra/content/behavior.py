from Products.CMFPlone.utils import safe_hasattr
from plone.app.content.interfaces import INameFromTitle
from plone.app.dexterity.behaviors.filename import NameFromFileName
from sllintra.content.interfaces import INameFromTitleOrFileName
from zope.component import adapts
from zope.interface import implements


class NameFromTitleOrFileName(NameFromFileName):
    implements(INameFromTitle)
    adapts(INameFromTitleOrFileName)

    def __new__(cls, context):
        if safe_hasattr(context, 'title') and not context.title:
            instance = super(NameFromTitleOrFileName, cls).__new__(cls, context)

        else:
            instance = super(NameFromFileName, cls).__new__(cls)
            instance.title = context.title

        return instance
