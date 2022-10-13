from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
)


class ChangeableItem(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBrush(QBrush(QColor("green")))
        self.setFlags(
            QGraphicsRectItem.ItemSendsGeometryChanges | QGraphicsRectItem.ItemIsMovable
        )

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            print("ChangeableItem", self.pos(), self.scenePos())
        return QGraphicsRectItem.itemChange(self, change, value)


app = QApplication([])
window = QMainWindow()
scene = QGraphicsScene(window)
view = QGraphicsView(scene)
view.setGeometry(0, 0, 500, 500)
scene.setSceneRect(0, 0, 500, 500)

rect_good = ChangeableItem(0, 0, 100, 100)
rect_bad = QGraphicsRectItem(100, 0, 100, 100)
rect_bad.setBrush(QBrush(QColor("blue")))


def patchItemChange(self, change, value):
    if change == QGraphicsRectItem.ItemPositionHasChanged:
        print("PatchedChangeableItem", self.pos(), self.scenePos())


# rect_bad.itemChange = Bull.patchItemChange
# rect_bad.setFlags(QGraphicsRectItem.ItemSendsGeometryChanges|QGraphicsRectItem.ItemIsMovable)
# print(rect_bad.brush().isOpaque())

scene.addItem(rect_good)
scene.addItem(rect_bad)
window.setCentralWidget(view)
window.resize(800, 800)
window.show()
app.exec_()
