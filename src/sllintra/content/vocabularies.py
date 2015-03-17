from plone.dexterity.interfaces import IDexterityFTI
from plone.schemaeditor.vocabularies import VocabulariesVocabulary as BaseVocabulary
from urlparse import urlparse
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.schema import Choice
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

        vocabulary = super(VocabulariesVocabulary, self).__call__(context)
        site = getSite()
        current_base_url = getMultiAdapter((site, site.REQUEST), name="plone_context_state").current_base_url()
        paths = urlparse(current_base_url).path.split('/')
        if paths[-3] == 'dexterity-types':
            name = u'{} - {}'.format(paths[-2], paths[-1])
            terms = vocabulary._terms
            for term in terms:
                if term.title == name:
                    terms.remove(term)
                    break
            vocabulary._terms = terms

        return vocabulary
