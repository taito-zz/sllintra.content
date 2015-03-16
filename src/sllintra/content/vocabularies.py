from plone.dexterity.interfaces import IDexterityFTI
from plone.schemaeditor.vocabularies import VocabulariesVocabulary as BaseVocabulary
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getSiteManager
from zope.component import getUtility
from zope.interface import implements
from zope.schema import Choice
from zope.schema import List
from zope.schema import Set
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


class SCVocabulary(object):
    implements(IVocabularyFactory)

    def __init__(self, name):
        names = name.split(' - ')
        self.fti = names[0]
        self.field = names[1]

    def __call__(self, context):
        fti = getUtility(IDexterityFTI, name=self.fti)
        schema = fti.lookupSchema()
        field = schema.get(self.field)
        if field is None:
            return SimpleVocabulary([SimpleTerm(value=None, title=None), ])
        elif isinstance(field, Choice):
            return field.vocabulary
        else:
            return field.value_type.vocabulary


class VocabulariesVocabulary(BaseVocabulary):

    """Vocabulary for a list of available vocabulary factories
    """

    def __call__(self, context):

        sm = getSiteManager(getSite())
        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        for fti in ftis:
            schema = fti.lookupSchema()
            for field_name in schema.names():
                field = schema.get(field_name)
                if isinstance(field, Set) or isinstance(field, List) or isinstance(field, Choice):
                    if context.__name__ != field.__name__:
                        name = '{} - {}'.format(fti.__name__, field.__name__)
                        sm.registerUtility(component=SCVocabulary(name), provided=IVocabularyFactory, name=name)

        return super(VocabulariesVocabulary, self).__call__(context)
