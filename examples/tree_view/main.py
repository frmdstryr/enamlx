# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
import cProfile,pstats,cStringIO

import enamlx
enamlx.install()

import enaml
from enaml.qt.qt_application import QtApplication

if __name__ == '__main__':
    with enaml.imports():
        from tree_view import Main

    app = QtApplication()
    view = Main()
    profiler = cProfile.Profile()
    profiler.enable()

    view.show()

    app.start()
    
    profiler.disable()
    s = cStringIO.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('time')
    ps.print_stats(100)
    print s.getvalue()
