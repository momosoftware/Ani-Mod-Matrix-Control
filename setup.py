from distutils.core import setup
import py2exe

setup(
    zipfile = None,
    console=[
        {
            'script':'ProjectorControl.py',
            'icon_resources': [(1, "avicon.ico")]
        }
    ],
)
