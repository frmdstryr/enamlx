# -*- coding: utf-8 -*-
'''
Created on Aug 31, 2015

@author: jrm
'''
import types
from atom.api import (Bool, Int, ForwardInstance, Instance, Typed)

from enamlx.widgets.plot_area import ProxyPlotArea
from enaml.qt.qt_control import QtControl
from enaml.qt.q_resource_helpers import get_cached_qcolor
import pyqtgraph as pg
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
from enaml.application import timed_call

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
            d = child.declaration
            kwargs = dict(row=d.row,col=d.column) if d.row or d.column else {}
            self.widget.addItem(child.widget,**kwargs)
        
    def child_removed(self, child):
        if isinstance(child,AbstractQtPlotItem):
            self.widget.removeItem(child.widget)

class AbstractQtPlotItem(QtControl):
    #: So we can receive signals
    __weakref__ = None
    
    #: Plot item or parent plot item if nested
    widget = Instance(pg.PlotItem)
    
    #: Actual plot
    plot = Instance(pg.GraphicsObject)
    
    #: Root or nested graph
    is_root = Bool()
    
    #: View box
    viewbox = Instance(pg.ViewBox)
    
    #: Axis item
    axis = Instance(pg.AxisItem)
    
    _pending_refreshes = Int(0)
    
    def create_widget(self):
        if isinstance(self.parent(),AbstractQtPlotItem):
            self.widget = self.parent_widget()
            self.is_root = False
        else:
            self.is_root = True
            self.widget = pg.PlotItem()

    def init_widget(self):
        #super(AbstractQtPlotItem, self).init_widget()
        d = self.declaration
        if self.is_root:
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
            if d.show_legend:
                self.set_show_legend(d.show_legend)
            if d.multi_axis:
                self.set_multi_axis(d.multi_axis)
            self.set_antialias(d.antialias)
            self.set_aspect_locked(d.aspect_locked)
            if d.background:
                self.set_background(d.background)
                
            if d.axis_left_ticks:
                self.set_axis_left_ticks(d.axis_left_ticks)
            
            if d.axis_bottom_ticks:
                self.set_axis_bottom_ticks(d.axis_bottom_ticks)
                
        self._refresh_plot()
        self.set_auto_range(d.auto_range)
        self.init_signals()
        
    def init_signals(self):
        self.widget.sigRangeChanged.connect(self.on_range_changed)
        self.widget.vb.sigResized.connect(self.on_resized)
    
    def _format_data(self):
        raise NotImplementedError
            
    def _format_style(self):
        data = {}
        d = self.declaration
        if d.line_pen:
            data['pen'] = d.line_pen
        if d.shadow_pen:
            data['shadowPen'] = d.shadow_pen
        if d.fill_level:
            data['fillLevel'] = d.fill_level
        if d.fill_brush:
            data['fillBrush'] = d.fill_brush
        if d.step_mode:
            data['stepMode'] = d.step_mode
        #if d.background:
        #    data['background'] = d.background
        if d.symbol:
            data['symbol'] = d.symbol
            if d.symbol_pen:
                data['symbolPen'] = d.symbol_pen
            if d.symbol_brush:
                data['symbolBrush'] = d.symbol_brush
            if d.symbol_size:
                data['symbolSize'] = d.symbol_size
            
        if d.antialias:
            data['antialias'] = d.antialias
            
        return data
        
    def _refresh_plot(self):
        """ Defer drawing until all changes are done so we don't draw
            during initialization or when many values change at once.
        """
        self._pending_refreshes+=1
        timed_call(100,self._redraw_plot)
        
    def _redraw_plot(self):
        self._pending_refreshes-=1
        if self._pending_refreshes!=0:
            return # Another change occurred
        
        if self.plot:
            self.plot.clear()
        if self.viewbox:
            self.viewbox.close()
        
        d = self.declaration
        
        data = self._format_data()
        style = self._format_style()

        if not self.is_root and d.parent.multi_axis:
            self._refresh_multi_axis()
            self.plot = self.viewbox.addItem(pg.PlotDataItem(*data,**style))
        else:  
            self.plot = self.widget.plot(*data,**style)
            
    def _refresh_multi_axis(self):
        """ If linked axis' are used, setup and link them """
        d = self.declaration
        
        #: Create a separate viewbox
        self.viewbox = pg.ViewBox()
        
        #: If this is the first nested plot, use the parent right axis
        _plots = [c for c in self.parent().children() if isinstance(c,AbstractQtPlotItem)]
        i = _plots.index(self)
        if i==0:
            self.axis = self.widget.getAxis('right') 
            self.widget.showAxis('right')
        else:
            self.axis = pg.AxisItem('right')
            self.axis.setZValue(-10000)
            
            #: Add new axis to scene
            self.widget.layout.addItem(self.axis,2,i+2)
        
        #: Link x axis to the parent axis
        self.viewbox.setXLink(self.widget.vb)
        
        #: Link y axis to the view
        self.axis.linkToView(self.viewbox)
        
        #: Set axis label
        self.axis.setLabel(d.label_right)
        
        #: Add Viewbox to parent scene
        self.parent().parent_widget().scene().addItem(self.viewbox)
        
    def set_row(self, row):
        self._refresh_plot()
    
    def set_column(self, column):
        self._refresh_plot()
    
    def set_aspect_locked(self,locked):
        return
        #self.widget.setAspectLocked(locked)
    
    def set_background(self, background):
        color = get_cached_qcolor(background) if background else None
        if isinstance(self.parent(), AbstractQtPlotItem):
            self.parent().parent_widget().setBackground(color)
        else:
            self.parent_widget().setBackground(color)
        
    def set_line_pen(self,pen):
        self.widget.setPen(pen)
        
    def set_shadow_pen(self,pen):
        self.widget.setShadowPen(pen)
    
    def set_axis_left_ticks(self,callback):
        self.set_axis_ticks('left', callback)
    
    def set_axis_bottom_ticks(self,callback):
        self.set_axis_ticks('bottom', callback)
    
    def set_axis_ticks(self,axis_name,callback):
        axis = self.widget.getAxis(axis_name)
        
        # Save ref 
        if not hasattr(axis, '_tickStrings'):
            axis._tickStrings = axis.tickStrings
        axis.tickStrings = types.MethodType(callback,axis,axis.__class__) if callback else axis._tickStrings
    
    def set_grid(self,grid):
        self.widget.showGrid(grid[0],grid[1],self.declaration.grid_alpha)
        
    def set_grid_alpha(self,alpha):
        self.set_grid(self.declaration.grid)
        
    def set_show_legend(self,show):
        if show:
            if not self.widget.legend:
                self.widget.addLegend()
        else:
            self.widget.legend.hide()
        
    def set_title(self,title):
        self.widget.setTitle(title)
        
    def set_label_top(self,text):
        self.widget.setLabels('top',text)
        
    def set_label_left(self,text):
        self.widget.setLabel('left',text)
        
    def set_label_right(self,text):
        if not self.is_root and self.declaration.parent.multi_axis:
            return # don't override multi axis label
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
    
    def on_resized(self):
        """ Update linked views """
        d = self.declaration
        if not self.is_root and d.parent.multi_axis:
            if self.viewbox:
                self.viewbox.setGeometry(self.widget.vb.sceneBoundingRect())
                self.viewbox.linkedViewChanged(self.widget.vb,self.viewbox.XAxis)
            
    
#     #
#     # Child events
#     #
#         
#     def child_added(self, child):
#         # TODO support layouts
#         if isinstance(child,AbstractQtPlotItem):
#             self.addItem(child.widget)
#         
#     def child_removed(self, child):
#         if isinstance(child,AbstractQtPlotItem):
#             self.removeItem(child.widget)

class QtPlotItem2D(AbstractQtPlotItem):
    
    def set_x(self,x):
        # Only refresh when they are equal
        # because one can be set at a time
        if len(self.declaration.y)==len(x):
            self._refresh_plot()
        
    def set_y(self,y):
        # Only refresh when they are equal
        # because one can be set at a time
        if len(self.declaration.x)==len(y):
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
            