from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from collective.base.interfaces import IAdapter
from datetime import datetime
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.z3cform import layout
from sllintra.content import _
from sllintra.content.form import AddArchiveForm
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.interfaces import HIDDEN_MODE
from zope.lifecycleevent import modified
from zope.schema import Text


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
            description = _(u'convert_archive_default_help', default=u'This value will be the default value for the newly converted archive content.')
            if widget != 'paths':
                self.widgets[widget].field.required = False
            if widget == 'IBasic.title':
                description = _(u'convert_archive_title_help', default=u'This value will be used for the newly converted archive content if the title is not set in the original content.')
            if widget == 'IBasic.description':
                description = _(u'convert_archive_description_help', default=u'This value will be used for the newly converted archive content if the description is not set in the original content.')
            if widget == self.file_field().getName():
                description = _(u'convert_archive_file_help', default=u'This file will be attached for the newly converted archive content if the file is not set in the original content.')
            if widget == 'image':
                description = _(u'convert_archive_image_help', default=u'This image will be attached for the newly converted archive content if the image is not set in the original content.')
            if widget == 'paivays':
                description = _(u'convert_archive_paivays_help', default=u'This value will be used for the newly converted archive content if the effective date is not set in the original content. If this value is empty and the effective date is not set, the creation date will be used for the new content.')
            if widget == 'text':
                description = _(u'convert_archive_text_help', default=u'This value will be used for the newly converted archive content if the text is not set in the original content.')
            self.widgets[widget].field.description = description

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
        file_field = self.file_field()
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


ConvertView = layout.wrap_form(ConvertForm)
