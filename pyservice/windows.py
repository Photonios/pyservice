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
import win32service
import win32serviceutil
import win32event
import win32api
from .platform_base import PyServicePlatformBase

class PyServiceWindows(PyServicePlatformBase, win32serviceutil.ServiceFramework):
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

        # Call the constructors of both base classes
        PyServicePlatformBase.__init__(self, *args)

        # Get the service class name (not sure why this is needed but whatever)
        self.compete_name = win32serviceutil.GetServiceClassString(self.service.__class__)

    def start(self):
        """Starts the service (if it's installed and not running).

        Returns:
            True when starting the service was a success and false when
            it failed.
        """

        win32serviceutil.StartService(self.name)

    def stop(self):
        """Stops the service (if it's installed and running).

        Returns:
            True when stopping the service was a success and false
            when it failed.
        """

        win32serviceutil.StopService(self.name)

    def install(self):
        """Installs the service so it can be started and stopped (if it's not installed yet).

        Returns:
            True when installing the service was a success and false
            when it failed.
        """

        # Build up wrapper script
        script_name = self.service.__class__.__name__
        module_name = win32serviceutil.GetServiceClassString(self.service.__class__)
        module_name = module_name.replace('.' + script_name, '')
        print(module_name)
        print(script_name)

        # Enable auto-start if needed
        service_start_type = None
        if self.auto_start:
            win32api.SetConsoleCtrlHandler(lambda control_handler: True, True)
            service_start_type = win32service.SERVICE_AUTO_START

        # Install the service
        win32serviceutil.InstallService(
            self.class_name,
            self.name,
            self.name,
            startType = service_start_type,
            description = self.description
        )

    def uninstall(self):
        """Uninstalls the service so it can no longer be used (if it's installed).

        Returns:
            True when installing the service was a success and false
            when it failed.
        """

        # Remove the service
        win32serviceutil.RemoveService(self.name)

    def is_installed(self):
        """Determines whether this service is installed on this system.

        Returns:
            True when this service is installed on this system and false
            when it was not installed on this system.
        """

        try:
            win32serviceutil.ChangeServiceConfig(self.class_name, self.name)
        except:
            return False
        return True

    def is_running(self):
        """Determines whether this service is running on this system.

        Returns:
            True when this service is running on this system and false
            when it was not running on this system.
        """

        # Read http://msdn.microsoft.com/en-us/library/windows/desktop/ms685996(v=vs.85).aspx
        # For a complete list of statues
        service_status = win32serviceutil.QueryServiceStatus(self.name)

        # Being paused or started (or one of their pending counter parts) is treated as running
        if service_status == win32service.SERVICE_RUNNING or \
                        service_status == win32service.SERVICE_START_PENDING or \
                        service_status == win32service.SERVICE_PAUSED or \
                        service_status == win32service.SERVICE_PAUSE_PENDING:
            return True

        # Not one of the start/paused states
        return False