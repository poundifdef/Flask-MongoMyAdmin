#from distutils.core import setup
from setuptools import setup, find_packages


setup(
    name='Flask-MongoMyAdmin',
    version='0.1',
    url='http://github.com/classicspecs/Flask-MongoMyAdmin/',
    author='Jay Goel',
    author_email='jay@classicspecs.com',
    description='Simple MongoDB Administrative Interface for Flask',
    long_description=open('README.rst').read(),
    #packages=['flask_mongomyadmin'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'pymongo',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

# To update pypi: `python setup.py register sdist upload`
