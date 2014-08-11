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
from .platform_base import PyServicePlatformBase

class PyServiceWindows(PyServicePlatformBase):
    """Implements service functionality on Windows.

    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the PyServiceWindows class.

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

        raise NotImplementedError('`install` not implemented in derived class')

    def uninstall(self):
        """Uninstalls the service so it can no longer be used (if it's installed).

        Returns:
            True when installing the service was a success and false
            when it failed.
        """

        raise NotImplementedError('`uninstall` not implemented in derived class')

    def is_installed(self):
        """Determines whether this service is installed on this system.

        Returns:
            True when this service is installed on this system and false
            when it was not installed on this system.
        """

        raise NotImplementedError('`is_installed` not implemented in derived class')

    def is_running(self):
        """Determines whether this service is running on this system.

        Returns:
            True when this service is running on this system and false
            when it was not running on this system.
        """

        raise NotImplementedError('`is_running` not implemented in derived class')