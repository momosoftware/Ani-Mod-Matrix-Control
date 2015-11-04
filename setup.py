from distutils.core import setup
import py2exe

setup(
    zipfile = None,
    options={'py2exe': {'bundle_files': 2, 'compressed': True, 'optimize': 2}},
    windows=[{'script':'ProjectorControl.py'}],
)
