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

    # def test_catalog__column__feed_order(self):
    #     catalog = getToolByName(self.portal, 'portal_catalog')
    #     self.assertIn('feed_order', catalog.schema())

    # def test_catalog__index__feed_order(self):
    #     from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
    #     catalog = getToolByName(self.portal, 'portal_catalog')
    #     self.assertIsInstance(catalog.Indexes['feed_order'], FieldIndex)

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

    def get_ctype(self, name):
        """Returns content type info.

        :param name: Name of content type.
        :type name: test_types__Plone_Site__filter_content_types
        """
        types = getToolByName(self.portal, 'portal_types')
        return types.getTypeInfo(name)

    def test_types__sllintra_content_Archive(self):
        ctype = self.get_ctype('sllintra.content.Archive')
        self.assertEqual(ctype.i18n_domain, 'sllintra.content')
        self.assertEqual(ctype.meta_type, 'Dexterity FTI')
        self.assertEqual(ctype.title, 'Archive')
        self.assertEqual(ctype.description, '')
        self.assertEqual(ctype.getIcon(), 'file.png')
        self.assertFalse(ctype.allow_discussion)
        self.assertTrue(ctype.global_allow)
        self.assertFalse(ctype.filter_content_types)
        self.assertEqual(ctype.schema, 'sllintra.content.schema.ArchiveSchema')
        self.assertEqual(ctype.klass, 'sllintra.content.content.Archive')
        self.assertEqual(ctype.add_permission, 'sllintra.content.AddArchive')
        self.assertEqual(ctype.behaviors, ())
        self.assertEqual(ctype.default_view, 'view')
        self.assertFalse(ctype.default_view_fallback)
        self.assertEqual(ctype.view_methods, ('view',))
        self.assertEqual(
            ctype.default_aliases,
            {'edit': '@@edit', 'sharing': '@@sharing', '(Default)': '(dynamic view)', 'view': '(selected layout)'})
        view = ctype.getActionObject('object/view')
        self.assertEqual(view.title, 'View')
        self.assertEqual(view.condition, '')
        self.assertEqual(view.getActionExpression(), 'string:${folder_url}/')
        self.assertTrue(view.visible)
        self.assertEqual(view.permissions, (u'View',))
        action = ctype.getActionObject('object/edit')
        self.assertEqual(action.title, 'Edit')
        self.assertEqual(action.condition, '')
        self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')
        self.assertTrue(action.visible)
        self.assertEqual(action.permissions, (u'sllintra.content: Edit Archive',))

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
