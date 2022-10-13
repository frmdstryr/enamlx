# -*- coding: utf-8 -*-
"""
Created on Aug 23, 2015

@author: jrm
"""
import faulthandler

import enaml
from enaml.qt.qt_application import QtApplication

import enamlx


def main():
    enamlx.install()

    faulthandler.enable()
    with enaml.imports():
        from table_view import Main

    app = QtApplication()
    view = Main()
    view.show()

    app.start()


if __name__ == "__main__":
    main()
