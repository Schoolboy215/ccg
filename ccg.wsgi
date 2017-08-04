import sys
activate_this = '/var/www/ccg/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, '/var/www/ccg/')
from app import app as application
