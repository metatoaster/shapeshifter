from setuptools import setup, find_packages
import os

try:
    import py2exe
except ImportError:
    pass

version = '0.7'

setup(
    name='shapeshifter',
    version=version,
    description='Shapeshifter (?) Parser?',
    long_description=open('README.rst').read() + "\n" +
                     open(os.path.join('docs', 'HISTORY.txt')).read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
    ],
    keywords='',
    author='Tommy Yu',
    author_email='y@metatoaster.com',
    url='http://metatoaster.com/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['shapeshifter'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    windows=[
        {
            'script': os.path.join('scripts', 'run.py',),
        }
    ],
    zipfile=None,
    options={
        'py2exe': {
            'includes': ['Tkinter'],
            'bundle_files': 1,
        }
    }
)
