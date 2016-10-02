'''
Created on Sep 26, 2016

@author: 

@from https://github.com/tpaviot/pythonocc-core/blob/master/src/addons/Display/qtDisplay.py

'''

import sys
import logging
from atom.api import Dict, Typed, Int, Property

from OCC.Display import OCCViewer

from ..widgets.occ_viewer import ProxyOccViewer

from enaml.qt import QtCore, QtGui, QtOpenGL
from enaml.qt.QtCore import Qt
from enaml.qt.qt_control import QtControl
from enaml.application import timed_call

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
# 
#     def initDriver(self):
#         self._display = OCCViewer.Viewer3d(self.GetHandle())
#         self._display.Create()
#         # background gradient
#         self._display.set_bg_gradient_color(206, 215, 222, 128, 128, 128)
#         # background gradient
#         self._display.display_trihedron()
#         self._display.SetModeShaded()
#         self._display.EnableAntiAliasing()
#         self._inited = True
#         # dict mapping keys to functions
#         self._SetupKeyMap()
#         #
#         self._display.thisown = False

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
    #: Viewer widget
    widget = Typed(QtViewer3d)
    
    #: Update count
    _update_count = Int(0)
    
    #: Displayed Shapes
    _displayed_shapes = Dict()
    
    #: Shapes
    shapes = Property(lambda self:self.get_shapes(),cached=True)
    
    @property
    def display(self):
        return self.widget._display
    
    def get_shapes(self):
        return [c for c in self.children()]
    
    def create_widget(self):
        self.widget = QtViewer3d(parent=self.parent_widget())
        
    def init_widget(self):
        d = self.declaration
        widget = self.widget
        
        #: Create viewer
        widget._display = OCCViewer.Viewer3d(widget.GetHandle())
        display = widget._display
        display.Create()        
        
        # background gradient
        self.set_background_gradient(d.background_gradient)
        self.set_trihedron_mode(d.trihedron_mode)
        self.set_display_mode(d.display_mode)
        self.set_selection_mode(d.selection_mode)
        self.set_view_mode(d.view_mode)
        self.set_antialiasing(d.antialiasing)
        self.set_double_buffer(d.double_buffer)
        self._update_raytracing_mode()
        
        #: Setup callbacks
        display.register_select_callback(self.update_selection)
        self.update_selection()
        
        widget._inited = True # dict mapping keys to functions
        widget._SetupKeyMap() #
        display.thisown = False
        
        
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
        timed_call(100,self.display.OnResize)
            
    def child_added(self, child):
        super(QtOccViewer, self).child_added(child)
        self.get_member('shapes').reset(self)
        child.observe('shape',self.update_display)
        self.update_display({'value':child.shape,
                             'type':'update',
                             'name':'shape',
                             'owner':child})
        
        
    def child_removed(self, child):
        super(QtOccViewer, self).child_removed(child)
        self.get_member('shapes').reset(self)
        child.unobserve('shape',self.update_display)
        
    def set_antialiasing(self, enabled):
        if enabled:
            self.display.EnableAntiAliasing()
        else:
            self.display.DisableAntiAliasing()
            
    def set_shadows(self, enabled):
        self._update_raytracing_mode()
        
    def set_reflections(self, enabled):
        self._update_raytracing_mode()
        
    def _update_raytracing_mode(self):
        d = self.declaration    
        display = self.display
        if not hasattr(display.View, 'SetRaytracingMode'):
            return
        if d.shadows or d.reflections:
         
            display.View.SetRaytracingMode()
            if d.shadows:
                display.View.EnableRaytracedShadows()
            if d.reflections:
                display.View.EnableRaytracedReflections()
            if d.antialiasing:
                display.View.EnableRaytracedAntialiasing()
        else:
            display.View.DisableRaytracingMode()
            
    def set_double_buffer(self, enabled):
        return # Enabled by default
        #self.display.SetDoubleBuffer(enabled)
        #self.widget.a
            
    def set_background_gradient(self, gradient):
        self.display.set_bg_gradient_color(*gradient)
        
    def set_trihedron_mode(self, mode):
        self.display.display_trihedron()
        
    def set_selection_mode(self, mode):
        if mode=='shape':
            self.display.SetSelectionModeShape()
        elif mode=='neutral':
            self.display.SetSelectionModeNeutral()
        elif mode=='face':
            self.display.SetSelectionModeFace()
        elif mode=='edge':
            self.display.SetSelectionModeEdge()
        elif mode=='vertex':
            self.display.SetSelectionModeVertex()
        
    def set_display_mode(self, mode):
        if mode=='shaded':
            self.display.SetModeShaded()
        elif mode=='hlr':
            self.display.SetModeHLR()
        elif mode=='wireframe':
            self.display.SetModeWireFrame()
    
    def set_view_mode(self, mode):
        if mode=='iso':
            self.display.View_Iso()
        elif mode=='top':
            self.display.View_Top()
        elif mode=='bottom':
            self.display.View_Bottom()
        elif mode=='left':
            self.display.View_Left()
        elif mode=='right':
            self.display.View_Right()
            
    def update_selection(self,*args,**kwargs):
        d = self.declaration
        selection = []
        for shape in self.display.selected_shapes:
            if shape in self._displayed_shapes:
                selection.append(self._displayed_shapes[shape].declaration)
            else:
                print "shape {} not in {}".format(shape,self._displayed_shapes)
        d.selection = selection
        
#     def _queue_update(self,change):
#         self._update_count +=1
#         timed_call(0,self._check_update,change)
#     
#     def _dequeue_update(self,change):
#         # Only update when all changes are done
#         self._update_count -=1
#         if self._update_count !=0:
#             return
#         self.update_shape(change)
            
    def update_display(self, change):
        self._update_count +=1
        timed_call(0,self._do_update)
        
    def clear_display(self):
        display = self.display
        # Erase all just HiDES them
        display.Context.PurgeDisplay()
        display.Context.RemoveAll()
        
    def _do_update(self):
        # Only update when all changes are done
        self._update_count -=1
        if self._update_count !=0:
            return
        #: TO
        display = self.display
        self.clear_display()
        displayed_shapes = {}
        for shape in self.shapes:
            update = shape==self.shapes[-1]
            d = shape.declaration
            s = shape.shape.Shape()
            displayed_shapes[s] = shape
            display.DisplayShape(s,
                                 color=d.color,
                                 transparency=d.transparency,
                                 update=update)
        self._displayed_shapes = displayed_shapes
    
    
