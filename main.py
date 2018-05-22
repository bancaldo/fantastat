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
Django for ORM only
Wx for graphics
"""

import os

# Django specific settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


import sys
# add the project path into the sys.path
sys.path.append(os.getcwd())
# add the virtualenv site-packages path to the sys.path
sys.path.append('venv/Lib/site-packages')


# noinspection PyUnresolvedReferences
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


if __name__ == '__main__':
    from players.controller import Controller
    c = Controller()
