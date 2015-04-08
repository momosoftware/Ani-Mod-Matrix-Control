from distutils.core import setup
import py2exe

setup(
    zipfile = None,
    console=[
        {
            'script':'ProjectorControl.py'
        }
    ],
)
