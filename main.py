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
Django 1.11 for ORM only
Wx 4 (Phoenix) for graphics
"""

import os

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


import sys
# add the project path into the sys.path
venv_path = '\\'.join([os.getcwd(), 'venv\\Lib\\site-packages'])
sys.path.append(os.getcwd())
# add the virtualenv site-packages path to the sys.path
sys.path.append(venv_path)
sys.path = [pth for pth in sys.path if 'wx-3' not in pth] # remove old wx-3


# noinspection PyUnresolvedReferences
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


if __name__ == '__main__':
    from players.controller import Controller
    c = Controller()
