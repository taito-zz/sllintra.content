from Acquisition import aq_inner
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.browser import add
from plone.dexterity.i18n import MessageFactory as DMF
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from sllintra.content import _
from z3c.form import button
from zope.component import getUtility


class AddArchiveForm(add.DefaultAddForm):

    portal_type = "sllintra.content.Archive"

    def add(self, object):

        container = aq_inner(self.context)
        new_object = addContentToContainer(container, object)

        if object.title is None and object.archive_file is None:

            container._delObject(new_object.id)
            self.immediate_view = '/'.join(container.getPhysicalPath())

        else:

            fti = getUtility(IDexterityFTI, name=self.portal_type)

            if fti.immediate_view:
                self.immediate_view = "/".join(
                    [container.absolute_url(), new_object.id, fti.immediate_view]
                )
            else:
                self.immediate_view = "/".join(
                    [container.absolute_url(), new_object.id]
                )

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

            if data['archive_file'] is None and data['title'] is None:
                message = _(u'You need to input title or add archive file to create Archive content type.')
                IStatusMessage(self.request).addStatusMessage(message, type='info')

            else:

                IStatusMessage(self.request).addStatusMessage(
                    DMF(u"Item created"), "info success"
                )


class AddArchiveView(add.DefaultAddView):

    form = AddArchiveForm
