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

import pyservice
import os
import stat
import sys
from .platform_base import PyServicePlatformBase

class PyServiceLinux(PyServicePlatformBase):
    """Implements service functionality (using deamons) on Linux.

    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the PyServiceLinux class.

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

        super().__init__(*args, **kwargs)

        # We store a start script in /etc/init.d, for now we don't support
        # system who don't have it
        if not os.path.exists('/etc/init.d'):
            raise pyservice.UnsupportedPlatformError('`/etc/init.d` does not exists, this is probably not a Debian based distribution.')

        # Make sure the path that PID files are stored in exists
        if not os.path.exists('/pids/'):
            os.mkdir('/pids/')

        # Build up some paths
        self.pid_file = '/pids/%s.pid' % self.name
        self.control_script = '/etc/init.d/%s' % self.name

    def start(self):
        """Starts the service (if it's installed and not running).

        Returns:
            True when starting the service was a success and false when
            it failed.
        """

        raise NotImplementedError('`start` not implemented in derived class')

    def stop(self):
        """Stops the service (if it's installed and running).

        Returns:
            True when stopping the service was a success and false
            when it failed.
        """

        raise NotImplementedError('`stop` not implemented in derived class')

    def install(self):
        """Installs the service so it can be started and stopped (if it's not installed yet).

        Returns:
            True when installing the service was a success and false
            when it failed.
        """

        # Make sure we're running with administrative privileges
        if os.getuid() != 0:
            raise pyservice.NoElevatedRightsError('We need power (aka root/sudo)')

        # Simple bash script to write to /etc/init.d
        start_script = """#!/bin/bash

                        PYTHON_PATH="%PYTHON_PATH%"
                        SERVICE_PATH="%SERVICE_PATH%"

                        case $1 in
                            start)
                                $PYTHON_PATH $SERVICE_PATH --start
                                ;;

                            stop)
                                $PYTHON_PATH $SERVICE_PATH --stop
                                ;;

                            restart)
                                $PYTHON_PATH $SERVICE_PATH --stop
                                $PYTHON_PATH $SERVICE_PATH --stop
                                ;;

                            *)
                                echo 'Unknown action, try; start/stop/restart\\n'
                        esac"""

        # Determine the path of the current script and the path to the python interpreter
        service_path = os.path.join(os.getcwd(), sys.argv[0])
        python_path = sys.executable

        # Replace the python path and the path to our service in the start script
        start_script = start_script.replace('%PYTHON_PATH%', python_path)
        start_script = start_script.replace('%SERVICE_PATH%', service_path)

        # Write the control script to file (/etc/init.d)
        file = open(self.control_script, 'w')
        file.write(start_script)
        file.close()

        # Make the file executable (chmod +x)
        stat = os.stat(self.control_script)
        os.chmod(self.control_script, stat.st_mode | 0o0111)
        return True

    def uninstall(self):
        """Uninstalls the service so it can no longer be used (if it's installed).

        Returns:
            True when installing the service was a success and false
            when it failed.
        """

        # Make sure we're running with administrative privileges
        if os.getuid() != 0:
            raise pyservice.NoElevatedRightsError('We need power (aka root/sudo)')


        # Remove the control script from /etc/init.d
        os.remove(self.control_script)
        return True

    def is_installed(self):
        """Determines whether this service is installed on this system.

        Returns:
            True when this service is installed on this system and false
            when it was not installed on this system.
        """

        return os.path.exists(self.control_script)

    def is_running(self):
        """Determines whether this service is running on this system.

        Returns:
            True when this service is running on this system and false
            when it was not running on this system.
        """

        return os.path.exists(self.pid_file)
