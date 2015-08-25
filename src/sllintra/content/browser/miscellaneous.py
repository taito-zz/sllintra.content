from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class Miscellaneous(BrowserView):

    def show_convert_button(self):
        context = aq_inner(self.context)
        return "Folder" in context.getRawImmediatelyAddableTypes()
