import enamlx
enamlx.install()

def occ_box_factory():
    from occ.occ_brep import OccBRepBox
    return OccBRepBox

from enaml.qt.qt_factories import QT_FACTORIES
QT_FACTORIES['BRepBox'] = occ_box_factory

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