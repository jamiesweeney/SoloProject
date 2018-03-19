activate_this = '/usr/share/SoloProject/server-env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Create appilcation for our app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app as application
