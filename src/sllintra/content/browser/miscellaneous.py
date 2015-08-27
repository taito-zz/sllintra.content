from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.ATContentTypes.interfaces import IATFolder


class Miscellaneous(BrowserView):

    def show_convert_button(self):
        context = aq_inner(self.context)
        return IATFolder.providedBy(context) and "Folder" in context.getRawImmediatelyAddableTypes()
