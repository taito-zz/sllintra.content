from Products.CMFCore.utils import getToolByName
from zope.component import getSiteManager
from zope.schema.interfaces import IVocabularyFactory
from zope.site.hooks import getSite

import logging


logger = logging.getLogger(__name__)
PROFILE_ID = 'profile-sllintra.content:default'


def unregister_vocabularies(setup):
    """Unregister vocabularies"""
    sm = getSiteManager(getSite())
    names = ['archive - vastaanottaja', 'arkistoitava_tiedosto - vastaanottaja', 'arkistoitu_tiedosto - aihepiiri', 'arkistoitu_tiedosto - sailytyspaikka']
    for name in names:
        sm.unregisterUtility(provided=IVocabularyFactory, name=name)
        message = '{} unregistered'.format(name)
        logger.info(message)


def reimport_actions(context):
    """Update actions"""
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'actions', run_dependencies=False, purge_old=False)
