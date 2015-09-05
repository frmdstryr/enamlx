# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''

import enamlx
enamlx.install()

import enaml
from enaml.qt.qt_application import QtApplication

if __name__ == '__main__':
    with enaml.imports():
        from tree_widget import Main

    app = QtApplication()
    view = Main()
    view.show()

    app.start()