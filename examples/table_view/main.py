# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
import faulthandler
import sys
sys.path.append('../../')

import enamlx
enamlx.install()

import enaml
from enaml.qt.qt_application import QtApplication

if __name__ == '__main__':
    faulthandler.enable()
    with enaml.imports():
        from table_view import Main

    app = QtApplication()
    view = Main()
    view.show()

    app.start()
