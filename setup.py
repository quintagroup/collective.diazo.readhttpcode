from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.md').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.diazo.readhttpcode',
      version=version,
      description="Middleware that allows augument Diazo theming with HTTP "
                  "status code returned by WSGI application being themed. "
                  "Extends functionality found in Diazo.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Development Status :: 4 - Beta",
          "Environment :: Web Environment",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
      ],
      keywords='diazo theme wsgi html xslt',
      author='Roman Kozlovskyi',
      author_email='kroman0@quintagroup.com',
      url='https://github.com/collective/collective.diazo.readhttpcode',
      license='gpl',
      packages=find_packages(),
      namespace_packages=['collective', 'collective.diazo'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=[
          'setuptools-git',
      ],
      install_requires=[
          'setuptools',
          'diazo[wsgi]',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_app_factory]
      main = collective.diazo.readhttpcode:ExtendedDiazoMiddleware
      """,
      )
