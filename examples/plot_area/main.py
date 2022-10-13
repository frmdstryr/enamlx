# -*- coding: utf-8 -*-
"""
Created on Aug 23, 2015

@author: jrm
"""
import enaml
from enaml.qt.qt_application import QtApplication

import enamlx


def main():
    enamlx.install()
    with enaml.imports():
        from plot_area import Main

    app = QtApplication()
    view = Main()
    view.show()

    app.start()


if __name__ == "__main__":
    main()
