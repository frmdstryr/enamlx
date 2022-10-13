import enaml
from enaml.qt.qt_application import QtApplication

import enamlx

if __name__ == "__main__":
    enamlx.install(allow_def=True)
    with enaml.imports():
        from graphics_items import Main

    app = QtApplication()
    view = Main()
    view.show()
    app.start()
