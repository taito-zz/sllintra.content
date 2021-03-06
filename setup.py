from setuptools import find_packages
from setuptools import setup


setup(
    name='sllintra.content',
    version='0.7.3',
    description="Provides content types for SLL intra site.",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"],
    keywords='',
    author='Taito Horiuchi',
    author_email='taito.horiuchi@abita.fi',
    url='https://github.com/taito/sllintra.content',
    license='None-free',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['sllintra'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.base',
        'collective.dexteritytextindexer',
        'plone.app.dexterity',
        'plone.app.versioningbehavior',
        'setuptools'],
    extras_require={'test': ['Products.PloneTestCase', 'Products.CMFPlacefulWorkflow', 'hexagonit.testing']},
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """)
