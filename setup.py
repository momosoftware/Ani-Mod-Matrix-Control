from distutils.core import setup
import py2exe

setup(
    zipfile = None,
    options = {'py2exe': {'bundle_files': 2, 'compressed': True}},
    windows=[{'script':'ProjectorControl.py'}],
)
