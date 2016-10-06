import enamlx
enamlx.install()

import occ

occ.install()

import enaml
from enaml.qt.qt_application import QtApplication

import cProfile


def main():
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
    