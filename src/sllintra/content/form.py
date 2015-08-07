from Acquisition import aq_inner
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.dexterity.i18n import MessageFactory as DMF
from plone.dexterity.interfaces import IDexterityEditForm
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.field import NamedBlobImage
from plone.z3cform import layout
from sllintra.content import _
from sllintra.content.interfaces import IArchive
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import classImplements
from plone.memoize import instance


def update_widget(instance):
    portal = instance.context.restrictedTraverse('@@plone_portal_state').portal()
    anno = IAnnotations(portal)
    name = 'sllintra.content.field_type'
    fields = anno.get(name)
    if fields:
        for name in fields:
            if fields[name] == u'radio' and instance.fields.get(name) is not None:
                instance.fields[name].widgetFactory = CheckBoxFieldWidget


class AddArchiveForm(add.DefaultAddForm):

    portal_type = "archive"

    @instance.memoize
    def file_field(self):
        """First file field"""
        file_field = None
        for field in self.fields.values():
            if isinstance(field.field, NamedBlobFile):
                file_field = field.field
                break
        return file_field

    @instance.memoize
    def image_field(self):
        """First image field"""
        image_field = None
        for field in self.fields.values():
            if isinstance(field.field, NamedBlobImage):
                image_field = field.field
                break
        return image_field

    def add(self, object):

        alsoProvides(object, IArchive)
        container = aq_inner(self.context)
        new_object = addContentToContainer(container, object)

        file_field = self.file_field()
        if object.title is None and getattr(object, file_field.getName()) is None:

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

    @button.buttonAndHandler(DMF('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

            file_field = self.file_field()
            if data[file_field.getName()] is None and data['IBasic.title'] is None:
                message = _(u'input_title_or_add_file', default=u'You need to input title or add file to create this content type.')
                IStatusMessage(self.request).addStatusMessage(message, type='info')

            else:

                IStatusMessage(self.request).addStatusMessage(
                    DMF(u"Item created"), "info success"
                )

    def updateWidgets(self):
        update_widget(self)
        super(AddArchiveForm, self).updateWidgets()


class AddArchiveView(add.DefaultAddView):

    form = AddArchiveForm


class EditArchiveForm(edit.DefaultEditForm):
    """"""

    def updateWidgets(self):
        update_widget(self)
        super(EditArchiveForm, self).updateWidgets()


EditArchiveView = layout.wrap_form(EditArchiveForm)
classImplements(EditArchiveView, IDexterityEditForm)
