from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from plone.schemaeditor.browser.field.edit import EditView as BaseEditView
from plone.schemaeditor.browser.field.edit import FieldEditForm as BaseFieldEditForm
from sllintra.content import _
from sllintra.content.vocabularies import SCVocabulary
from z3c.form import button
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.i18nmessageid import MessageFactory
from zope.schema import Choice
from zope.schema import List
from zope.schema import Set
from zope.schema.interfaces import IVocabularyFactory
from zope.site.hooks import getSite


PMF = MessageFactory('plone')


class FieldEditForm(BaseFieldEditForm):

    @button.buttonAndHandler(PMF(u'Save'), name='save')
    def handleSave(self, action):
        if isinstance(self.field, Set) or isinstance(self.field, List) or isinstance(self.field, Choice):
            data, errors = self.extractData()
            if data.get('vocabularyName') is None and data.get('values') is None:
                self.field.vocabularyName = None
                self.field.value_type.vocabularyName = None
                message = _(u'values_or_vocabulary_missing', default=u'You need to input values or select vocabulary.')
                site = getSite()
                IStatusMessage(site.REQUEST).addStatusMessage(message, type='info')
                url = getMultiAdapter((site, site.REQUEST), name="plone_context_state").current_page_url()
                return site.REQUEST.response.redirect(url)
            else:
                sm = getSiteManager(getSite())
                name = '{} - {}'.format(aq_parent(aq_inner(self.context)).__name__, self.field.__name__)
                if data.get('vocabularyName') is not None and data.get('values') is None:
                    sm.unregisterUtility(provided=IVocabularyFactory, name=name)
                else:
                    vocabulary = SCVocabulary(name)
                    sm.registerUtility(component=vocabulary, provided=IVocabularyFactory, name=name)

        super(FieldEditForm, self).handleSave(self, action)


class EditView(BaseEditView):
    form = FieldEditForm
