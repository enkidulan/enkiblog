import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()


setup(
    name='enkiblog',
    version='0.0',
    description='enkiblog',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",

    ],
    author='',
    author_email='',
    url='',
    keywords='web websauna pyramid',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    test_suite='enkiblog',
    install_requires=[
        'websauna',
        'python-slugify',
        'repoze.workflow',
        'babel',
        'pyramid_raven',
        'pyramid_mako',  # unpinned pyramid_raven dependency
        'pyramid_chameleon',
        'pyramid-layout',
    ],
    extras_require={
        'test': [
            'websauna[test]',
            'zope.deprecation',
            'pylint',
            'tox',
            'virtualenv',
            'factory_boy',
            'selenium',
            'testfixtures',
            'boom',
        ],
        'dev': [
            'websauna[dev]',
            'websauna[utils]',
            'ipython',
            'isort',
        ],
        'serving': [
            'gunicorn',
            'circus',
        ],
    },

    # Define where this application starts as referred by WSGI web servers
    entry_points="""\
    [paste.app_factory]
    main = enkiblog:main

    [console_scripts]
    createcontent = enkiblog.scripts.createcontent:main
    """,
)
