from Products.CMFCore.utils import getToolByName
from sllintra.content.tests.base import IntegrationTestCase


def get_roles(context, permission):
    return sorted([item['name'] for item in context.rolesOfPermission(permission) if item['selected'] == 'SELECTED'])


class TestCase(IntegrationTestCase):
    """TestCase for Plone setup."""

    def test_installed__package(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(installer.isProductInstalled('sllintra.content'))

    def test_browserlayer(self):
        from sllintra.content.browser.interfaces import ISllintraContentLayer
        from plone.browserlayer import utils
        self.assertIn(ISllintraContentLayer, utils.registered_layers())

    def test_metadata__version(self):
        setup = getToolByName(self.portal, 'portal_setup')
        self.assertEqual(
            setup.getVersionForProfile('profile-sllintra.content:default'), u'0')

    def test_metadata__installed__plone_app_dexterity(self):
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.failUnless(installer.isProductInstalled('plone.app.dexterity'))

    def test_rolemap__sllintra_content_Add_Archive(self):
        permission = "sllintra.content: Add Archive"
        self.assertEqual(get_roles(self.portal, permission), [
            'Manager',
            'Site Administrator'])
        self.assertEqual(self.portal.acquiredRolesAreUsedBy(permission), '')

    def test_rolemap__sllintra_content_Edit_Archive(self):
        permission = "sllintra.content: Edit Archive"
        self.assertEqual(get_roles(self.portal, permission), [
            'Manager',
            'Site Administrator'])
        self.assertEqual(self.portal.acquiredRolesAreUsedBy(permission), '')

    def uninstall_package(self):
        """Uninstall package: sllintra.content."""
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        installer.uninstallProducts(['sllintra.content'])

    def test_uninstall__package(self):
        self.uninstall_package()
        installer = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertFalse(installer.isProductInstalled('sllintra.content'))

    def test_uninstall__browserlayer(self):
        self.uninstall_package()
        from sllintra.content.browser.interfaces import ISllintraContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(ISllintraContentLayer, utils.registered_layers())
