# -*- coding: utf-8 -*-
'''
Created on Aug 31, 2015

@author: jrm
'''
from atom.api import (ForwardInstance,Instance, Typed)

from enamlx.widgets.plot_area import ProxyPlotArea
from enaml.qt.qt_control import QtControl
from enaml.qt.QtCore import QRect,QPoint
from pyqtgraph.graphicsItems.PlotItem.PlotItem import PlotItem
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem
from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject

def gl_view_widget():
    from pyqtgraph.opengl import GLViewWidget
    return GLViewWidget


class QtPlotArea(QtControl, ProxyPlotArea):
    """ PyQtGraph Plot Widget """
    __weakref__ = None
    widget = Typed(GraphicsLayoutWidget)
    
    def create_widget(self):
        self.widget = GraphicsLayoutWidget(self.parent_widget())
        
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
        
    def child_added(self, child):
        # TODO support layouts
        if isinstance(child,AbstractQtPlotItem):
            self.widget.addItem(child.widget)
        
    def child_removed(self, child):
        if isinstance(child,AbstractQtPlotItem):
            self.widget.removeItem(child.widget)

class AbstractQtPlotItem(QtControl):
    __weakref__ = None
    widget = Instance(PlotItem)
    plot = Instance(GraphicsObject)
    
    def create_widget(self):
        if isinstance(self.parent(),AbstractQtPlotItem):
            self.widget = self.parent_widget()
        else:
            self.widget = PlotItem()

    def init_widget(self):
        #super(AbstractQtPlotItem, self).init_widget()
        d = self.declaration
        if d.grid:
            self.set_grid(d.grid)
        if d.title:
            self.set_title(d.title)
        if d.label_left:
            self.set_label_left(d.label_left)
        if d.label_right:
            self.set_label_right(d.label_right)
        if d.label_top:
            self.set_label_top(d.label_top)
        if d.label_bottom:
            self.set_label_bottom(d.label_bottom)
        self.set_antialias(d.antialias)
        self.set_aspect_locked(d.aspect_locked)
        self._refresh_plot()
        self.set_auto_range(d.auto_range)
        
        self.init_signals()
        
    def init_signals(self):
        self.widget.sigRangeChanged.connect(self.on_range_changed)
        
    def _format_data(self):
        raise NotImplementedError
            
    def _format_style(self):
        data = {}
        if self.declaration.line_pen:
            data['pen'] = self.declaration.line_pen
        if self.declaration.shadow_pen:
            data['shadowPen'] = self.declaration.shadow_pen
        if self.declaration.fill_level:
            data['fillLevel'] = self.declaration.fill_level
        if self.declaration.fill_brush:
            data['fillBrush'] = self.declaration.fill_brush
        if self.declaration.step_mode:
            data['stepMode'] = self.declaration.step_mode
        if self.declaration.background:
            data['background'] = self.declaration.background
            print("BACKGROUND SET")
            
        if self.declaration.symbol:
            data['symbol'] = self.declaration.symbol
            if self.declaration.symbol_pen:
                data['symbolPen'] = self.declaration.symbol_pen
            if self.declaration.symbol_brush:
                data['symbolBrush'] = self.declaration.symbol_brush
            if self.declaration.symbol_size:
                data['symbolSize'] = self.declaration.symbol_size
            
        if self.declaration.antialias:
            data['antialias'] = self.declaration.antialias
            
        return data
        
    def _refresh_plot(self):
        if self.plot:
            self.plot.clear()
        #if not isinstance(self.parent(),AbstractQtPlotItem):
        #    print(self.widget.items)
        #self.widget.clear()
        
        data = self._format_data()
        style = self._format_style()
        
        self.plot = self.widget.plot(*data,**style)
    
    def set_aspect_locked(self,locked):
        return
        #self.widget.setAspectLocked(locked)
    
    def set_background(self, background):
        self._refresh_plot()
        #self.widget.setBackground(background)
        
    def set_line_pen(self,pen):
        return
        #self.widget.setPen(pen)
        
    def set_shadow_pen(self,pen):
        return
        #self.widget.setShadowPen(pen)
    
    def set_grid(self,grid):
        self.widget.showGrid(grid[0],grid[1],self.declaration.grid_alpha)
        
    def set_grid_alpha(self,alpha):
        self.set_grid(self.declaration.grid)
        
    def set_title(self,title):
        self.widget.setTitle(title)
        
    def set_label_top(self,text):
        self.widget.setLabels('top',text)
        
    def set_label_left(self,text):
        self.widget.setLabel('left',text)
        
    def set_label_right(self,text):
        self.widget.setLabel('right',text)
        
    def set_label_bottom(self,text):
        self.widget.setLabel('bottom',text)
    
    def set_auto_downsampling(self,enabled):
        self.widget.setDownsampling(auto=enabled)
        
    def set_antialias(self,enabled):
        self._refresh_plot()
    
    def set_auto_range(self,auto_range):
        d = self.declaration
        if not isinstance(auto_range, tuple):
            auto_range = (auto_range,auto_range)
            self.declaration.auto_range = auto_range
        if not auto_range[0]:
            self.set_range_x(d.range_x)
        if not auto_range[1]:
            self.set_range_y(d.range_y)
    # 
    # Setters that require a full refresh
    #    
    
    def set_symbol(self,arg):
        self._refresh_plot()
        
    def set_symbol_size(self,arg):
        self._refresh_plot()
        
    def set_symbol_brush(self,arg):
        self._refresh_plot()
        
    def set_fill_brush(self,arg):
        self._refresh_plot()
        
    def set_fill_level(self,arg):
        self._refresh_plot()
        
    def set_multi_axis(self,arg):
        self._refresh_plot()
        
    def set_log_mode(self,arg):
        self._refresh_plot()
    
    def set_clip_to_view(self,arg):
        self._refresh_plot()
        
    def set_step_mode(self,arg):
        self._refresh_plot()
        
    def set_range_x(self,val):
        """ Set visible range of x data. 
        
        Note: Padding must be 0 or it will create an infinite loop
        
        """
        d = self.declaration
        if d.auto_range[0]:
            return
        self.widget.setXRange(*val,padding=0)
        
    def set_range_y(self,val):
        """ Set visible range of y data. 
        
        Note: Padding must be 0 or it will create an infinite loop
        
        """
        d = self.declaration
        if d.auto_range[1]:
            return
        self.widget.setYRange(*val,padding=0)
        
    #
    # Widget events
    #
    def on_range_changed(self,vb,rect):
        d = self.declaration
        d.range_x = rect[0]
        d.range_y = rect[1]
    
    def on_scale_changed(self,view_scale):
        pass
    
    #
    # Child events
    #
        
    def child_added(self, child):
        # TODO support layouts
        if isinstance(child,AbstractQtPlotItem):
            self.addItem(child.widget)
        
    def child_removed(self, child):
        if isinstance(child,AbstractQtPlotItem):
            self.removeItem(child.widget)

class QtPlotItem2D(AbstractQtPlotItem):
    
    def set_x(self,x):
        self._refresh_plot()
        
    def set_y(self,y):
        self._refresh_plot()
        
    def _format_data(self):
        data = [self.declaration.y]
        if self.declaration.x is not None:
            data.insert(0,self.declaration.x)
        return data
    
        
class QtPlotItemDict(QtPlotItem2D):
    def set_data(self,data):
        self._refresh_plot()

    def _format_data(self):
        return self.declaration.data

class QtPlotItemList(QtPlotItemDict):
    pass
        
    
class QtPlotItemArray(QtPlotItem2D):
    pass

class QtPlotItem3D(QtPlotItem2D):
    """ Use forward instance to not cause import issues if 
    not installed. """
    widget = ForwardInstance(gl_view_widget)
    
    def create_widget(self):
        from pyqtgraph.opengl import GLViewWidget
        if isinstance(self.parent(),AbstractQtPlotItem):
            self.widget = self.parent_widget()
        else:
            self.widget = GLViewWidget(parent=self.parent_widget())
            self.widget.opts['distance'] = 40
            self.widget.raise_()
            
    def init_signals(self):
        pass

    def _create_grid(self):
        from pyqtgraph.opengl import GLGridItem
        gx = GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.widget.addItem(gx)
        gy = GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.widget.addItem(gy)
        gz = GLGridItem()
        gz.translate(0, 0, -10)
        self.widget.addItem(gz)
        
    def set_z(self,z):
        self._refresh_plot()
        
    def _refresh_plot(self):
        import numpy as np
        #import pyqtgraph as pg
        from pyqtgraph import opengl as gl
        
        self._create_grid()
        pts = np.vstack([self.declaration.x,self.declaration.y,self.declaration.z]).transpose()
        plt = gl.GLLinePlotItem(pos=pts)#, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
        self.widget.addItem(plt)
        
    def set_grid(self,grid):
        pass
        
    
        

class QtPlotItemArray3D(QtPlotItem3D):
    def _refresh_plot(self):
        import numpy as np
        import pyqtgraph as pg
        from pyqtgraph import opengl as gl
        
        self._create_grid()
        n = 51
        x = self.declaration.x
        y = self.declaration.y
        for i in range(n):
            yi = np.array([y[i]]*100)
            d = (x**2 + yi**2)**0.5
            z = 10 * np.cos(d) / (d+1)
            pts = np.vstack([x,yi,z]).transpose()
            plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
        self.widget.addItem(plt)
        
        

#     def set_data(self,data):
#         self.widget.plotItem.clear()
#         if self._views:
#             for view in self._views:
#                 view.clear()
#             
#         views = []
#         i = 0
#         if self.declaration.multi_axis:
#             for i,plot in enumerate(data):
#                 if i>3:
#                     break
#                 if 'pen' not in plot:
#                     plot['pen'] = self._colors[i]
#                 if i>0:
#                     view = ViewBox()
#                     views.append(view)
#                     self.widget.plotItem.scene().addItem(view)
#                     if i==1:
#                         axis = self.widget.plotItem.getAxis('right')
#                     elif i>1:
#                         axis = AxisItem('right')
#                         axis.setZValue(-10000)
#                         self.widget.plotItem.layout.addItem(axis,2,3)
#                     axis.linkToView(view)
#                     view.setXLink(self.widget.plotItem)
#                     view.addItem(PlotCurveItem(**plot))
#                 else:    #view.setYLink(self.widget.plotItem)
#                     self.widget.plot(**plot)
#         if i>0:
#             def syncViews():
#                 for v in views:
#                     v.setGeometry(self.widget.plotItem.vb.sceneBoundingRect())
#                     v.linkedViewChanged(self.widget.plotItem.vb,v.XAxis)
#             syncViews()
#             self.widget.plotItem.vb.sigResized.connect(syncViews)
#         self._views = views
            