######################################################################################
#
#   This file is part of PyService.
#
#   PyService is free software: you can redistribute it and/or modify it under the
#   terms of the GNU General Public License as published by the Free Software
#   Foundation, version 2.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#   details.
#
#   You should have received a copy of the GNU General Public License along with
#   this program; if not, write to the Free Software Foundation, Inc., 51
#   Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#   Copyright: Swen Kooij (Photonios) <photonios@outlook.com>
#
#####################################################################################

import sys

class PyService(object):
    """Interface for classes who wish to represent a service.

    By overriding virtual methods, the deriving class that perform
    actions when certain event occur, such as a starting or stopping of the
    service, or install and uninstalling it.

    By passing the program's command line arguments, PyService can take care
    of handling parameters such as `--start` and `--install`.

    """

    def __init__(self, name, description, auto_start):
        """Initializes a new instance of the PyService class.

        This will parse specified command line options and will handle the
        following command line parameters:

        * --install
        * --uninstall
        * --start
        * --stop
        * --run

        Based on the specified command line parameters, the associated action
        will be taken.

        If none of the command line parameters above is specified, it will default
        to `--run` which will run the program without being installed as a service.

        Args:
            name (str):
                The name of the service, this name is used when installing or looking
                for the service.
            description (str):
                Small sentence, describing this service.
            auto_start (bool):
                True when this service needs to be started automatically when the system
                starts or when the service crashes.

        """

        # Maps command line options to functions
        self.option_map = {
            '--install': self._install,
            '--uninstall': self._uninstall,
            '--start': self._start,
            '--stop': self._stop,
            '--run': self.start
        }

        # Store constructor parameters
        self.name = name
        self.description = description
        self.auto_start = auto_start

        # Are there any command line parameters?
        cmd_option = '--run'
        if len(sys.argv) > 1:
            cmd_option = sys.argv[1]

        # Is this a valid command line parameter?
        if cmd_option not in self.option_map:
            cmd_option = '--run'

        # Call the associated function
        self.option_map[cmd_option]()

    def start(self):
        pass

    def stop(self):
        pass

    def install(self):
        pass

    def uninstall(self):
        pass

    def _start(self):
        print('_start')
        pass

    def _stop(self):
        print('_stop')
        pass

    def _install(self):
        print('_install')
        pass

    def _uninstall(self):
        print('_uninstall')
        pass