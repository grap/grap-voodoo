# -*- coding: utf-8 -*-
import sys
# Import libs that are not in the docker image, using same technic as
# in /bin/start_openerp
sys.path[0:0] = [
    '../eggs/ERPpeek-1.6.3-py2.7.egg',
    '../eggs/psutil-5.4.3-py2.7-linux-x86_64.egg',
]
import erppeek
import psutil
