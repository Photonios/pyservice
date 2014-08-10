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
import atexit
import signal
import time
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
        pid_files_directory = os.path.join(os.path.expanduser('~'), '.pyservice_pids')
        if not os.path.exists(pid_files_directory):
            os.mkdir(pid_files_directory)

        # Build up some paths
        self.pid_file = os.path.join(pid_files_directory, self.name + '.pid')
        self.control_script = '/etc/init.d/%s' % self.name

    def start(self):
        """Starts the service (if it's installed and not running).

        Returns:
            True when starting the service was a success and false when
            it failed.
        """

        # Attempt to fork parent process (double fork)
        try:
            pid = os.fork()
            if pid > 0:
                    sys.exit(0)
        except OSError as error:
            print('* Unable to fork parent process (1): %s' % format(error))
            return False

        # Decouple from parent environment
        os.setsid()
        os.umask(0)

        # Do the second fork
        try:
            pid = os.fork()
            if pid > 0:
                    sys.exit(0)
        except OSError as error:
            print('* Unable to fork parent process (2): %s' % format(error))
            return False

        # Register cleanup function
        atexit.register(self._clean)
        atexit.register(self.service.stopped)

        # Write the PID file
        pid = str(os.getpid())
        try:
            file = open(self.pid_file, 'w')
            file.write(str(pid) + '\n')
            file.close()
        except Exception as error:
            print('* Unable to write PID file to `%s`: %s' % self.pid_file, format(error))
            return False

        # Redirect standard file descriptors to /dev/null
        sys.stdout.flush()
        sys.stdin.flush()
        standard_in = open(os.devnull, 'r')
        standard_out = open(os.devnull, 'a+')
        standard_error = open(os.devnull, 'a+')

        os.dup2(standard_in.fileno(), sys.stdin.fileno())
        os.dup2(standard_out.fileno(), sys.stdout.fileno())
        os.dup2(standard_error.fileno(), sys.stderr.fileno())
        return True

    def stop(self):
        """Stops the service (if it's installed and running).

        Returns:
            True when stopping the service was a success and false
            when it failed.
        """

        # Attempt to read the PID from the pid file
        file = open(self.pid_file, 'r')

        try:
            pid = int(file.read().strip())
        except:
            print("* Unable to read PID file")
            return False

        file.close()

        # Remove the PID file already to indicate that this is a stop
        # and not abnormal program termination, when the PID file is still
        # the service will handle this as abnormal program termination
        # and will restart the service if auto-start is enabled
        os.remove(self.pid_file)

        # Attempt to kill the process, continue to attempt to kill it until
        # the process has died with a maximum of 5 attempts
        attempts = 0
        try:

            while attempts < 5:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.2)
                attempts += 1

        except OSError as error:
            error_message = str(error.args)

            # Check the error message, if it contains the text below,
            # the process is no longer running and we have thus killed the process
            if error_message.find("No such process") > 0:
                return True
            else:
                print("* Unable to kill the process %s" % error_message)
                return False

        # We were unable to kill the process due to an unknown reason
        print("* Unable to kill the process due to an unknown reason")
        return False

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
                                $PYTHON_PATH $SERVICE_PATH --start
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
        try:
            os.remove(self.control_script)
        except Exception as error:
            print("* Unable to uninstall, failed to remove control script: %s" % str(error))
            return False

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

    def _clean(self):
        """This is the cleanup function we register for the forked process.

        This function is called when the process ends. This way we can clean
        up stuff etc.

        By checking whether the PID file still exists, we can detect whether
        this is a normal stop, or whether we're dealing with abnormal program
        termination.

        Note: This does not prevent SIGKILL, if SIGKILL is signalled, we're dead
        for real. The only way we can back up then is the cron job
        """

        # If the PID file still exists, we're dealing with abnormal program
        # termination and we'll restart ourselves if auto-start is enabled
        if os.path.exists(self.pid_file) and self.auto_start:
            service_path = os.path.join(os.getcwd(), sys.argv[0])
            os.remove(self.pid_file)
            time.sleep(1)
            os.system(sys.executable + ' ' + service_path + ' --start')

        # Normal program termination (aka service stopped)
        return
