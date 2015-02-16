from persistent.dict import PersistentDict
from plone.app.dexterity import MessageFactory as _
from plone.app.dexterity.browser.fields import EnhancedSchemaListing
from plone.app.dexterity.browser.fields import TypeFieldsPage
from plone.schemaeditor.browser.schema.listing import ReadOnlySchemaListing
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.schemaeditor.interfaces import ISchemaContext
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import component
from zope import interface
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import ISet
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


class EnhancedSchemaListing(EnhancedSchemaListing):
    """"""

    def updateWidgets(self):
        for fid in self.fields:
            field = self.fields[fid]
            if isinstance(field.field, schema.Set) and IFieldType(field.field).field_type == u'radio':
                field.widgetFactory = CheckBoxFieldWidget
        super(EnhancedSchemaListing, self).updateWidgets()


class TypeFieldsPage(TypeFieldsPage):

    @property
    def form(self):
        if self.context.fti.hasDynamicSchema:
            return EnhancedSchemaListing
        else:
            return ReadOnlySchemaListing


field_types = SimpleVocabulary([SimpleTerm(value=u'radio', title=_(u'Radio button field')), SimpleTerm(value=u'select', title=_(u'Select field'))])


class IFieldType(interface.Interface):

    field_type = schema.Choice(
        title=_(u'Field type'),
        description=_(u'Select field type'),
        required=True,
        default=u'select',
        vocabulary=field_types)


@interface.implementer(IFieldEditorExtender)
@component.adapter(ISchemaContext, ISet)
def getFieldType(schema_context, field):
    return IFieldType


class FieldTypeAdapter(object):
    component.adapts(ISet)
    implements(IFieldType)

    def __init__(self, field):
        self.field = field

    def _get_field_type(self):
        portal = getSite()
        anno = IAnnotations(portal)
        name = 'sllintra.content.field_type'
        if anno.get(name) is None:
            anno[name] = PersistentDict()
        field_type = anno.get(name)
        return field_type.get(self.field.getName(), 'select')

    def _set_field_type(self, value):
        portal = getSite()
        anno = IAnnotations(portal)
        name = 'sllintra.content.field_type'
        if anno.get(name) is None:
            anno[name] = PersistentDict()
        anno[name].update({self.field.getName(): value})

    field_type = property(_get_field_type, _set_field_type)


schema.Set.field_type = FieldProperty(IFieldType['field_type'])
