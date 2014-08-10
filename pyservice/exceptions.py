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

class UnsupportedPlatformError(Exception):
    """Thrown when an error was detected that determined that this platform is not supported.

    This could happen for example when you're running an custom Linux distribution, or
    simply a distribution that is not supported.
    """

    def __init__(self, message):
        """Initializes a new instance of the UnsupportedPlatformError class.

        Args:
            message (str):
                A message describing the cause of the error.
        """

        self.message = message

    def __str__(self):
        return self.message

class NoElevatedRightsError(Exception):
    """Thrown when elevated rights (root/Admin) were required by not given."""

    def __init__(self, message):
        """Initializes a new instance of the NoElevatedRightsError class.

        Args:
            message (str):
                A message describing the cause of the error.
        """

        self.message = message

    def __str__(self):
        return self.message

class AlreadyInstalledError(Exception):
    """Thrown when a service was already installed and another installation attempt was made."""

    def __init__(self, message):
        """Initializes a new instance of the AlreadyInstalledError class.

        Args:
            message (str):
                A message describing the cause of the error.
        """

        self.message = message

    def __str__(self):
        return self.message