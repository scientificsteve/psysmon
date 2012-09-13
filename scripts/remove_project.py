#!/usr/bin/env python

# License
#     This file is part of Seismon.
#
#     If you use Seismon in any program or publication, please inform and
#     acknowledge its author Stefan Mertl (info@stefanmertl.com). 
# 
#     Seismon is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
Remove a project completely.
This includes the file structure and the database tables.

:copyright:
    Stefan Mertl

:license:
    GNU General Public License, Version 3 
    (http://www.gnu.org/licenses/gpl-3.0.html)
'''

import sys
from psysmon.core.test_util import clear_project

def run():
    if len(sys.argv) <= 2:
        print "At least 2 arguments required.\n"
        sys.exit()

    project_file = sys.argv[1]
    user_name = sys.argv[2]

    if len(sys.argv) == 4:
        user_pwd = sys.argv[3]
    else:
        user_pwd = ''

    clear_project(project_file, user_name, user_pwd)


if __name__ == '__main__':
    run()




