#!/usr/bin/python
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_dir)

reload(sys)
sys.setdefaultencoding("utf-8")

import logging
logging.basicConfig(stream=sys.stderr)

activate_this = '/home/intercp/www/ga-web/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from gaweb import app as application

if __name__=="__main__":
  application.run(host='0.0.0.0', debug=True)
