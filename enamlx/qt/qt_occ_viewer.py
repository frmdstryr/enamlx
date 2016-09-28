'''
Created on Sep 26, 2016

@author: 

@from https://github.com/tpaviot/pythonocc-core/blob/master/src/addons/Display/qtDisplay.py

'''

import sys
import logging
from atom.api import Typed

from OCC.Display import OCCViewer

from ..widgets.occ_viewer import ProxyOccViewer

from enaml.qt import QtCore, QtGui, QtOpenGL
from enaml.qt.QtCore import Qt
from enaml.qt.qt_control import QtControl

log = logging.getLogger(__name__)

class QtBaseViewer(QtOpenGL.QGLWidget):
    ''' The base Qt Widget for an OCC viewer
    '''

    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self._display = None
        self._inited = False

        # enable Mouse Tracking
        self.setMouseTracking(True)
        # Strong focus
        self.setFocusPolicy(Qt.WheelFocus)

        # required for overpainting the widget
        self.setAttribute(Qt.WA_PaintOnScreen)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAutoFillBackground(False)

    def GetHandle(self):
        ''' returns an the identifier of the GUI widget.
        It must be an integer
        '''
        win_id = self.winId()  # this returns either an int or voitptr

        if "%s"%type(win_id) == "<type 'PyCObject'>":  # PySide
            ### with PySide, self.winId() does not return an integer
            if sys.platform == "win32":
                ## Be careful, this hack is py27 specific
                ## does not work with python31 or higher
                ## since the PyCObject api was changed
                import ctypes
                ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
                ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [
                    ctypes.py_object]
                win_id = ctypes.pythonapi.PyCObject_AsVoidPtr(win_id)
        elif type(win_id) is not int:  #PyQt4 or 5
            ## below integer cast may be required because self.winId() can
            ## returns a sip.voitptr according to the PyQt version used
            ## as well as the python version
            win_id = int(win_id)
        return win_id

    def resizeEvent(self, event):
        if self._inited:
            self._display.OnResize()


class QtViewer3d(QtBaseViewer):
    def __init__(self, *args,**kwargs):
        super(QtViewer3d, self).__init__(*args, **kwargs)
        self._drawbox = False
        self._zoom_area = False
        self._select_area = False
        self._inited = False
        self._leftisdown = False
        self._middleisdown = False
        self._rightisdown = False
        self._selection = None
        self._drawtext = True

    def initDriver(self):
        self._display = OCCViewer.Viewer3d(self.GetHandle())
        self._display.Create()
        # background gradient
        self._display.set_bg_gradient_color(206, 215, 222, 128, 128, 128)
        # background gradient
        self._display.display_trihedron()
        self._display.SetModeShaded()
        self._display.EnableAntiAliasing()
        self._inited = True
        # dict mapping keys to functions
        self._SetupKeyMap()
        #
        self._display.thisown = False

    def _SetupKeyMap(self):
        def set_shade_mode():
            self._display.DisableAntiAliasing()
            self._display.SetModeShaded()

        self._key_map = {ord('W'): self._display.SetModeWireFrame,
                         ord('S'): set_shade_mode,
                         ord('A'): self._display.EnableAntiAliasing,
                         ord('B'): self._display.DisableAntiAliasing,
                         ord('H'): self._display.SetModeHLR,
                         ord('F'): self._display.FitAll,
                         ord('G'): self._display.SetSelectionMode}

    def keyPressEvent(self, event):
        code = event.key()
        if code in self._key_map:
            self._key_map[code]()
        else:
            msg = "key: {0}\nnot mapped to any function".format(code)
            
            log.info(msg)

    def Test(self):
        if self._inited:
            self._display.Test()

    def focusInEvent(self, event):
        if self._inited:
            self._display.Repaint()

    def focusOutEvent(self, event):
        if self._inited:
            self._display.Repaint()

    def paintEvent(self, event):
        if self._inited:
            self._display.Context.UpdateCurrentViewer()
            # important to allow overpainting of the OCC OpenGL context in Qt
            self.swapBuffers()

        if self._drawbox:
            self.makeCurrent()
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))
            rect = QtCore.QRect(*self._drawbox)
            painter.drawRect(rect)
            painter.end()
            self.doneCurrent()

    def resizeGL(self, width, height):
        self.setupViewport(width, height)

    def ZoomAll(self, evt):
        self._display.FitAll()

    def wheelEvent(self, event):
        try:  # PyQt4/PySide
            delta = event.delta()
        except:  # PyQt5
            delta = event.angleDelta().y()
        if delta > 0:
            zoom_factor = 2
        else:
            zoom_factor = 0.5
        self._display.Repaint()
        self._display.ZoomFactor(zoom_factor)

    def dragMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        self.setFocus()
        self.dragStartPos = event.pos()
        self._display.StartRotation(self.dragStartPos.x(), self.dragStartPos.y())

    def mouseReleaseEvent(self, event):
        pt = event.pos()
        modifiers = event.modifiers()

        if event.button() == Qt.LeftButton:
            pt = event.pos()
            if self._select_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.SelectArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._select_area = False
            else:
                # multiple select if shift is pressed
                if modifiers == Qt.ShiftModifier:
                    self._display.ShiftSelect(pt.x(), pt.y())
                else:
                    # single select otherwise
                    self._display.Select(pt.x, pt.y)
        elif event.button() == Qt.RightButton:
            
            if self._zoom_area:
                [Xmin, Ymin, dx, dy] = self._drawbox
                self._display.ZoomArea(Xmin, Ymin, Xmin + dx, Ymin + dy)
                self._zoom_area = False

    def DrawBox(self, event):
        tolerance = 2
        pt = event.pos()
        dx = pt.x() - self.dragStartPos.x()
        dy = pt.y() - self.dragStartPos.y()
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            return
        self._drawbox = [self.dragStartPos.x(), self.dragStartPos.y(), dx, dy]
        self.update()

    def mouseMoveEvent(self, evt):
        pt = evt.pos()
        buttons = int(evt.buttons())
        modifiers = evt.modifiers()
        # ROTATE
        if (buttons == Qt.LeftButton and
                not modifiers == Qt.ShiftModifier):
            dx = pt.x() - self.dragStartPos.x()
            dy = pt.y() - self.dragStartPos.y()
            self._display.Rotation(pt.x(), pt.y())
            self._drawbox = False
        # DYNAMIC ZOOM
        elif (buttons == Qt.RightButton and
              not modifiers == Qt.ShiftModifier):
            self._display.Repaint()
            self._display.DynamicZoom(abs(self.dragStartPos.x()),
                                      abs(self.dragStartPos.y()), abs(pt.x()),
                                      abs(pt.y()))
            self.dragStartPos = pt
            self._drawbox = False
        # PAN
        elif buttons == Qt.MidButton:
            dx = pt.x() - self.dragStartPos.x()
            dy = pt.y() - self.dragStartPos.y()
            self.dragStartPos = pt
            self._display.Pan(dx, -dy)
            self._drawbox = False
        # DRAW BOX
        # ZOOM WINDOW
        elif (buttons == Qt.RightButton and
              modifiers == Qt.ShiftModifier):
            self._zoom_area = True
            self.DrawBox(evt)
        # SELECT AREA
        elif (buttons == Qt.LeftButton and
              modifiers == Qt.ShiftModifier):
            self._select_area = True
            self.DrawBox(evt)
        else:
            self._drawbox = False
            self._display.MoveTo(pt.x(), pt.y())
            
class QtOccViewer(QtControl,ProxyOccViewer):
    widget = Typed(QtViewer3d)
    
    def create_widget(self):
        self.widget = QtViewer3d(parent=self.parent_widget())
        
    def init_widget(self):
        self.widget.initDriver()
        
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
        
            
    def child_added(self, child):
        super(QtOccViewer, self).child_added(child)
        child.observe('shape',self.update_display)
        self.update_display({'value':child.shape,
                             'type':'update',
                             'name':'shape',
                             'owner':child})
        
    def child_removed(self, child):
        super(QtOccViewer, self).child_removed(child)
        child.unobserve('shape',self.update_display)
        
    def update_display(self, change):
        #: TO
        display = self.widget._display
        display.EraseAll()
        shapes = [c.shape.Shape() for c in self.children()]
        for i,s in enumerate(shapes):
            update = i+1==len(shapes)
            display.DisplayShape(s, update=update)
