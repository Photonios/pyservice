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
import tornado.ioloop
import tornado.web
import sys

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello world!')

class MyService(pyservice.PyService):
    def started(self):
        application = tornado.web.Application([
            (r'/', TestHandler)
        ])

        application.listen(1337)
        tornado.ioloop.IOLoop.instance().start()

    def stopped(self):
        sys.exit(0)
        pass

    def installed(self):
        pass

    def uninstalled(self):
        pass

if __name__ == '__main__':
    MyService('myservice', 'My nice little test service', True)