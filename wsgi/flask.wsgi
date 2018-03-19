import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Virtualenv settings
activate_this = '/usr/share/SoloProject/server-env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Create appilcation for our app
from app import app as application
