activate_this = "/home/ubuntu/py37/bin/activate_this.py"
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, "/home/ubuntu/flask")
from nmail import app as application
