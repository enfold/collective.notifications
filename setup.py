# coding=utf-8
from setuptools import find_packages
from setuptools import setup

version = '0.1'

setup(
    name='collective.notifications',
    version=version,
    description=(
        "Provides notifications for users."
    ),
    long_description="%s\n" % (
        open("README.rst").read(),
    ),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent"
    ],
    keywords='Plone Notifications',
    author='enfold',
    author_email='info@enfoldsystems.com',
    url='http://svn.plone.org/svn/collective/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'z3c.jbot',
    ],
    extras_require={
        'async': [
            'plone.app.async',
        ]
    },
    entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone

      [celery_tasks]
      notify = collective.notifications.tasks
      """
)
