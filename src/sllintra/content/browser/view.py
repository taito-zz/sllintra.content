from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.statusmessages.interfaces import IStatusMessage
from collective.base.interfaces import IAdapter
from datetime import datetime
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.dexterity.browser.base import DexterityExtensibleForm
from plone.dexterity.i18n import MessageFactory as DMF
from plone.dexterity.interfaces import IDexterityEditForm
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.z3cform import layout
from sllintra.content import _
from sllintra.content.form import AddArchiveForm
from sllintra.content.form import update_widget
from sllintra.content.interfaces import IArchive
from z3c.form import button
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.field import Fields
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import classImplements
from zope.lifecycleevent import modified
from zope.schema import List
from zope.schema import Text
from z3c.form.interfaces import HIDDEN_MODE


paths_field = Text(__name__='paths', title=_(u'Paths'), readonly=True)


class ConvertForm(AddArchiveForm):
    """Base form to convert"""

    label = _(u'Convert')
    ignoreContext = True

    def updateWidgets(self):
        super(ConvertForm, self).updateWidgets()
        if self.paths and isinstance(self.paths, list):
            self.widgets['paths'].value = '\n'.join(self.paths)
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['IVersionable.changeNote'].mode = HIDDEN_MODE
        for widget in self.widgets:
            if widget != 'paths':
                self.widgets[widget].field.required = False

    def update(self):
        self.paths = self.request.form.get('paths') or self.request.form.get('form.widgets.paths')
        if self.paths is None:
            message = _(u'select_items_to_archive', default=u'Select the content items to be archived.')
            IStatusMessage(self.request).addStatusMessage(message, type='info')
            url = '{}/folder_contents'.format(self.context.absolute_url())
            return self.request.response.redirect(url)
        self.fields += Fields(paths_field)
        return super(ConvertForm, self).update()

    @button.buttonAndHandler(_(u'Convert'), name='convert')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # 1. Create folder where selected items will be archived.
        fid = 'converted-archives'
        ftitle = u'Converted Archives'
        number = 0
        while self.context.get(fid) is not None:
            number += 1
            if number != 1:
                fid.split('-')[:2]
                fid = '-'.join(fid.split('-')[:2])
                ftitle = ' '.join(ftitle.split(' ')[:2])
            fid = '{}-{}'.format(fid, number)
            ftitle = '{} {}'.format(ftitle, number)

        self.context.invokeFactory('Folder', fid, title=ftitle)
        folder = self.context[fid]

        # 2. Find original objects.
        adapter = IAdapter(self.context)
        paths = self.paths.split('\n')
        objs = self.context.getObjectsFromPathList(paths)
        form = self.request.form

        # Data from form
        title = form.get('form.widgets.IBasic.title')
        description = form.get('form.widgets.IBasic.description')
        fpaivays = None
        if form.get('form.widgets.paivays-year') and form.get('form.widgets.paivays-day'):
            fpaivays = datetime(int(form.get('form.widgets.paivays-year')),
                int(form.get('form.widgets.paivays-month')), int(form.get('form.widgets.paivays-day')))
        text = form.get('form.widgets.text')
        asiakirjan_luonne = form.get('form.widgets.asiakirjan_luonne')
        aihepiiri = form.get('form.widgets.aihepiiri')

        # file
        file_data = None
        file_name = None
        file_field = self._file_field()
        name = 'form.widgets.{}'.format(file_field.getName())
        cfile = form.get(name)
        if cfile:
            cfile.seek(0)
            file_data = cfile.read()
            file_name = cfile.filename
            cfile.close()

        # image
        image_data = None
        image_name = None
        cimage = form.get('form.widgets.image')
        if cimage:
            cimage.seek(0)
            image_data = cimage.read()
            image_name = cimage.filename
            cimage.close()

        # 3. Select values and create archive.
        for obj in objs:
            data = {}
            data['title'] = obj.Title() or title
            data['description'] = obj.Description() or description
            uuid = obj.UID()
            brain = adapter.get_brain(UID=uuid)
            paivays = fpaivays
            if brain.review_state == 'published':
                paivays = brain.effective
            if paivays is None:
                paivays = brain.created
            if not isinstance(paivays, datetime):
                paivays = paivays.asdatetime().replace(tzinfo=None)
            data['paivays'] = paivays
            if obj.getField('text') is not None:
                text = safe_unicode(obj.getField('text').get(obj)) or text
            if text:
                data['text'] = text
            if form.get('form.widgets.asiakirjan_luonne') is not None:
                data['asiakirjan_luonne'] = asiakirjan_luonne
            if form.get('form.widgets.aihepiiri') is not None:
                data['aihepiiri'] = aihepiiri

            # file
            ofile = obj.getField('file', obj)
            if ofile and ofile.get(obj).get_size():
                filedata = ofile.get(obj).data
                filename = safe_unicode(ofile.get(obj).filename)
            else:
                filedata = file_data
                filename = file_name
            if file_data is not None and file_name is not None:
                data['arkistoitava_tiedosto'] = NamedBlobFile(data=filedata, filename=safe_unicode(filename))

            # image
            oimage = obj.getField('image', obj)
            if oimage and oimage.get(obj).get_size():
                imagedata = oimage.get(obj).data
                imagename = safe_unicode(oimage.get(obj).filename)
            else:
                imagedata = image_data
                imagename = image_name
            if image_data is not None:
                if imagename is not None:
                    imagename = safe_unicode(imagename)
                data['image'] = NamedBlobImage(data=imagedata, filename=imagename)

            content = createContentInContainer(folder, 'archive', checkConstraints=False, **data)
            modified(content)

        message = _(u"add_converted_archives_success", default=u"${number} converted archive(s) are added to folder: ${title}",
            mapping={'number': len(objs), 'title': ftitle})
        IStatusMessage(self.request).addStatusMessage(message, type='info')

        url = '{}/folder_contents'.format(self.context.absolute_url())
        return self.request.response.redirect(url)

        # obj = self.createAndAdd(data)
        # if obj is not None:
        #     # mark only as finished if we get the new object
        #     self._finishedAdd = True

        #     file_field = self._file_field()
        #     if data[file_field.getName()] is None and data['IBasic.title'] is None:
        #         message = _(u'input_title_or_add_file', default=u'You need to input title or add file to create this content type.')
        #         IStatusMessage(self.request).addStatusMessage(message, type='info')

        #     else:

        #         IStatusMessage(self.request).addStatusMessage(
        #             DMF(u"Item created"), "info success"
        #         )



ConvertView = layout.wrap_form(ConvertForm)
