'''
Created on Sep 28, 2016

@author: jrm
'''
import enamlx
import faulthandler
enamlx.install()

import occ

occ.install()

import enaml
from enaml.qt.qt_application import QtApplication

import cProfile
import sys
import logging


def main():
    logging.basicConfig(level='DEBUG',stream=sys.stdout,format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s')
    
    try:
        import faulthandler
        faulthandler.enable()
    except ImportError:
        pass
        

    with enaml.imports():
        from view import Main

    app = QtApplication()
    profiler = cProfile.Profile()
    
    view = Main()
    view.show()

    # Start the application event loop
    profiler.enable()
    app.start()
    profiler.disable()
    profiler.print_stats('tottime')


if __name__ == "__main__":
    main()
    