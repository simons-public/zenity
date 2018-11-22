""" Installer for python zenity API """

from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='zenity',
    version='1.0.0',
    description='Simple python API for zenity',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/simons-public/zenity',
    author='Chris Simons',
    author_email='chris@simonsmail.net',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Environment :: X11 Applications',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: BSD License',
        ],
    keywords='zenity',
    packages=['zenity'],
    zip_safe=True,
)

