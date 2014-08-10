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
import platform
import pyservice

from .linux import PyServiceLinux

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
            '--run': self.started
        }

        # Maps systems/platforms to the right classes
        self.platform_map = {
            'Linux': PyServiceLinux
        }

        # Store constructor parameters
        self.name = name
        self.description = description
        self.auto_start = auto_start

        # Determine whether this platform is supported
        if platform.system() not in self.platform_map:
            print('* Unsupported platform: `%s`' % platform.system())
            return

        # Create a new instance of the platform specific class
        try:
            self.platform_impl = self.platform_map[platform.system()](self, self.name, self.description, self.auto_start)
        except Exception as error:
            print('* Error: %s' % str(error))
            return

        # Are there any command line parameters?
        cmd_option = '--run'
        if len(sys.argv) > 1:
            cmd_option = sys.argv[1]

        # Is this a valid command line parameter?
        if cmd_option not in self.option_map:
            cmd_option = '--run'

        # Call the associated function, if something went wrong, exit with 1
        try:
            if not self.option_map[cmd_option]():
                sys.exit(1)
        except Exception as error:
            print(str(error))
            sys.exit(1)

    def started(self):
        """Virtual, to be overridden by the derived class.

        Called when the service is starting, the derived class should
        start some kind of blocking loop now to prevent the service
        from stopping.
        """

        raise NotImplementedError('`started` not implemented in derived class')

    def stopped(self):
        """Virtual, to be overridden by the derived class.

        Called when the service is stopping, the derived class should attempt
        to stop the blocking loop it created/started when the service was
        starting.
        """

        raise NotImplementedError('`stopped` not implemented in derived class')

    def installed(self):
        """Virtual, to be overridden by the derived class.

        Called when the service is being installed, this gives the derived class
        the chance to prepare some stuff.
        """

        raise NotImplementedError('`installed` not implemented in derived class')

    def uninstalled(self):
        """Virtual, to be overridden by the derived class.

        Called when the service is being uninstalled, this gives the derived class
        the chance to reverse anything that was installed during the installation.
        """

        raise NotImplementedError('`uninstalled` not implemented in derived class')

    def is_installed(self):
        """Determines whether this service is installed on this system.

         Returns:
            True when this service is installed on this system and false
            when it was not installed on this system.
        """

        return self.platform_impl.is_installed()

    def is_running(self):
        """Determines whether this service is running on this system.

        Returns:
            True when this service is running on this system and false
            when it was not running on this system.
        """

        return self.platform_impl.is_running()

    def _start(self):
        """Starts this service.

        Handles this by requesting a start from the platform specific implementation.

        Returns:
            True when starting the service was a success and false when it failed.
        """

        # Make sure the service is not already running
        if self.platform_impl.is_running():
            print('* Already running')
            return False

        # Attempt to start the service
        print('* Starting %s' % self.name)
        result = self.platform_impl.start()

        # Call event handler
        self.started()
        return result

    def _stop(self):
        """Stop this service.

        Handles this by requesting a stop from the platform specific implementation.

        Returns:
            True when stopping the service was a success and false when it failed.
        """

        # Make sure that the service is running
        if not self.platform_impl.is_running():
            print('* Not running')
            return False

        # Attempt to stop the service
        print('* Stopping %s' % self.name)
        result = self.platform_impl.stop()

        # We do not call the event handler (self.stop()) here because we are killing a forked
        # process, stopped() will be called when the python script exits
        return result

    def _install(self):
        """Installs this service.

        Handles this by requesting an installation from the platform specific implementation.

        Returns:
            True when installing the service was a success and false when it failed.
        """

        # Make sure the service is not already installed
        if self.platform_impl.is_installed():
            print('* Already installed')
            return False

        # Attempt to install the service
        print('* Installing %s' % self.name)
        result = self.platform_impl.install()

        # Call event handler
        self.installed()
        return result

    def _uninstall(self):
        """Uninstalls this service.

        Handles this by requesting an un-installation from the platform specific implementation.

        Returns:
            True when un-installing the service was a success and false when it failed.
        """

        # Make sure the service is installed
        if not self.platform_impl.is_installed():
            print('* Not installed')
            return False

        # Attempt to uninstall the service
        print('* Uninstalling %s' % self.name)
        result = self.platform_impl.uninstall()

        # Call event handler
        self.uninstalled()
        return result