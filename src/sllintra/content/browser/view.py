from OFS.Image import Pdata
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
from sllintra.content.interfaces import IArchive
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.interfaces import HIDDEN_MODE
from zope.interface import alsoProvides
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

        # 1. Find or create folder where selected items will be archived.
        folder_id = "{}-converted".format(self.context.id)
        folder_title = "{} Converted".format(self.context.Title())
        folder = self.context.get(folder_id)
        if folder is None:
            folder = self.context[self.context.invokeFactory('Folder', folder_id, title=folder_title)]

        # 2. Find original objects.
        adapter = IAdapter(self.context)
        paths = self.paths.split('\r\n') if '\r\n' in self.paths else self.paths.split('\n')
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

        omits = ['form.widgets.IBasic.title',
        'form.widgets.IBasic.description',
        'form.widgets.paivays-year',
        'form.widgets.paivays-month',
        'form.widgets.paivays-day',
        'form.widgets.text',
        'form.widgets.text.mimeType',
        'form.buttons.convert',
        'form.widgets.paivays-empty-marker',
        'form.widgets.paivays-calendar',
        'form.widgets.IVersionable.changeNote',
        'form.widgets.paths']

        # file
        file_field = self.file_field()
        fname = 'form.widgets.{}'.format(file_field.getName())
        cfile = form.get(fname)
        omits.append(fname)
        if cfile:
            cfile.seek(0)
            file_data = cfile.read()
            file_name = cfile.filename
            cfile.close()

        # image
        image_field = self.image_field()
        iname = 'form.widgets.{}'.format(image_field.getName())
        cimage = form.get(iname)
        omits.append(iname)
        if cimage:
            cimage.seek(0)
            image_data = cimage.read()
            image_name = cimage.filename
            cimage.close()

        keys = [key for key in form.keys() if key not in omits and key.startswith('form.widgets.') and not key.endswith('empty-marker')]
        data = {}
        for key in keys:
            val = form.get(key)
            if val:
                if isinstance(val, list):
                    val = [va.decode('unicode_escape') for va in val]
                data[key.split('.')[2]] = val

        object_ids = []
        # 3. Select values and create archive.
        for obj in objs:
            data = data.copy()
            data['title'] = safe_unicode(obj.Title()) or title
            data['description'] = safe_unicode(obj.Description()) or description
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

            content = createContentInContainer(folder, 'archive', checkConstraints=False, **data)

            # file
            filedata = None
            contentType = ''
            ofile = obj.getField('file', obj)
            if ofile:
                file_obj = ofile.get(obj)
                if file_obj and file_obj.get_size():
                    filedata = file_obj.data
                    filename = file_obj.filename or data['title']
                    contentType = file_obj.getContentType()

            if filedata is None and cfile:
                filedata = file_data
                filename = file_name

            if filedata is not None:
                setattr(content, file_field.getName(), NamedBlobFile(data=filedata, filename=safe_unicode(filename), contentType=contentType))

            # image
            imagedata = None
            contentType = ''
            oimage = obj.getField('image', obj)
            if oimage:
                image_obj = oimage.get(obj)
                if image_obj and image_obj.get_size():
                    imagedata = image_obj.data if not isinstance(image_obj.data, Pdata) else image_obj.data.data
                    imagename = safe_unicode(image_obj.filename) or data['title']
                    contentType = image_obj.getContentType()

            if imagedata is None and cimage:
                imagedata = image_data
                imagename = image_name

            if imagedata is not None:
                setattr(content, image_field.getName(), NamedBlobImage(data=imagedata, filename=safe_unicode(imagename), contentType=contentType))

            alsoProvides(content, IArchive)
            modified(content)

            object_ids.append(obj.id)
        # Remove the original object
        self.context.manage_delObjects(object_ids)

        message = _(u"add_converted_archives_success", default=u"${number} converted archive(s) are added to folder: ${title}",
            mapping={'number': len(objs), 'title': safe_unicode(folder_title)})
        IStatusMessage(self.request).addStatusMessage(message, type='info')

        url = '{}/folder_contents'.format(self.context.absolute_url())
        return self.request.response.redirect(url)


ConvertView = layout.wrap_form(ConvertForm)
