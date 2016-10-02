import enamlx
enamlx.install()

import occ

occ.install()

import enaml
from enaml.qt.qt_application import QtApplication


def main():
    with enaml.imports():
        from view import Main

    app = QtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()


if __name__ == "__main__":
    main()
    