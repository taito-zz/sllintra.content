from plone.app.dexterity.interfaces import ITypeSchemaContext
from plone.dexterity.interfaces import IDexterityFTI
from plone.schemaeditor.utils import FieldRemovedEvent
from zope.component import adapter
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getSiteManager
from zope.component import queryUtility
from zope.schema import Choice
from zope.schema import List
from zope.schema import Set
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


@adapter(ITypeSchemaContext, FieldRemovedEvent)
def unregister_vocabulary(context, event):
    assert context == event.object
    name = u'{} - {}'.format(context.__name__, event.field.__name__)
    vocabulary = queryUtility(IVocabularyFactory, name=name)
    if vocabulary is not None:
        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        for fti in ftis:
            schema = fti.lookupSchema()
            for field_name in schema.names():
                field = schema.get(field_name)
                if isinstance(field, Set) or isinstance(field, List) or isinstance(field, Choice):
                    if getattr(field, 'vocabularyName', None) == name:
                        field.vocabularyName = None
                        field.value_type.vocabularyName = None
                        field.value_type.vocabulary = SimpleVocabulary.fromValues([None, ])

        sm = getSiteManager(getSite())
        sm.unregisterUtility(provided=IVocabularyFactory, name=name)
