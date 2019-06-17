import sys
sys.path.append('../../')
import enamlx
enamlx.install(allow_def=True)

import enaml
from enaml.qt.qt_application import QtApplication

if __name__ == '__main__':
    with enaml.imports():
        from graphics_items import Main

    app = QtApplication()
    view = Main()
    view.show()
    app.start()

