import sys
import os

os.environ['SERVER_SECRET'] = "var"
os.environ['SERVER_MYSQL_PATH'] = "var"
os.environ['SERVER_SSL_CA'] = "var"
os.environ['SERVER_SSL_CENT'] = "var"
os.environ['SERVER_SSL_KEY'] = "var"
os.environ['SERVER_SB_HOST'] = "var"
os.environ['SERVER_SB_USERNAME'] = "var"
os.environ['SERVER_SB_PASSWORD'] = "var"
os.environ['SERVER_SSL_NAME'] = "var"

# Create appilcation for our app
sys.path.append('usr/share/SoloProject/src/server')
from app import app as application
