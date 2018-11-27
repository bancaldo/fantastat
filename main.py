"""
Manages player evaluations and shows average values of players

SYNOPSIS
========
::
python main.py

DESCRIPTION
===========
Import evaluations MagicCup files and shows players values as
fanta_vote average, vote average, rate of played matches,
player cost

Modules
=====
Django for ORM and db
Wxfor graphics
"""

import os

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import sys
# add the project path into the sys.path
working_dir = os.getcwd()
sys.path.append(working_dir)

import platform
# add the virtualenv site-packages path to the sys.path
VENV_PATH = '/venv/Lib/site-packages' if platform.system() == 'Linux' else\
             r'\venv\Lib\site-packages'
sys.path.append(os.getcwd() + VENV_PATH)

# noinspection PyUnresolvedReferences
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import wx
from players.controller import Controller


class App(wx.App):
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def OnInit(self):
        from settings import DATABASES
        db = DATABASES.get('default').get('NAME')
        if db not in os.listdir(os.getcwd()):
            from django.core.management import call_command
            print("INFO: db 'players.db' not found")
            print("INFO: invoking django 'makemigrations' command...")
            call_command("makemigrations", interactive=False)
            print("INFO: invoking django 'migrate' command...")
            call_command("migrate", interactive=False)
        Controller()
        return True


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
