# -*- coding: utf-8 -*-
'''
Created on Jun 11, 2015

@author: jrm
'''
from atom.atom import set_default
from atom.api import (Callable, Tuple, Instance, Enum, Float, ContainerList, Bool, FloatRange, Unicode, Dict, Typed, ForwardTyped, observe)
from enaml.core.declarative import d_
from enaml.widgets.api import Container
from enaml.widgets.control import Control, ProxyControl
from atom.instance import ForwardInstance

def numpy_ndarray():
    import numpy
    return numpy.ndarray

class ProxyPlotArea(ProxyControl):
    declaration = ForwardTyped(lambda: PlotArea)
    
        
class PlotArea(Container):
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')
    proxy = Typed(ProxyPlotArea)
    setup = d_(Callable(lambda graph:None))
    
PEN_ARGTYPES = (tuple,list,basestring,dict)
BRUSH_ARGTYPES = (tuple,list,basestring,dict,int,float)

class PlotItem(Control):
    #setup = Callable()
    name = d_(Unicode())
    line_pen = d_(Instance(PEN_ARGTYPES))
    shadow_pen = d_(Instance(PEN_ARGTYPES))
    #line_connect = d(Instance())
    
    fill_level = d_(Float(strict=False))
    
    # ‘c’     one of: r, g, b, c, m, y, k, w
    # R, G, B, [A]     integers 0-255
    #(R, G, B, [A])     tuple of integers 0-255
    # float     greyscale, 0.0-1.0
    # int     see intColor()
    # (int, hues)     see intColor()
    # “RGB”     hexadecimal strings; may begin with ‘#’
    # “RGBA”      
    # “RRGGBB”      
    # “RRGGBBAA”      
    fill_brush = d_(Instance(BRUSH_ARGTYPES))   
    
    symbol = d_(Enum(None,'o', 's', 't', 'd', '+'))
    symbol_size = d_(Float(10,strict=False))
    symbol_pen = d_(Instance(PEN_ARGTYPES))
    symbol_brush = d_(Instance(BRUSH_ARGTYPES))
    #symbol_brush = d_()
    
    title = d_(Unicode())
    label_left = d_(Unicode())
    label_right = d_(Unicode())
    label_top = d_(Unicode())
    label_bottom = d_(Unicode())
    
    # H, V
    grid = d_(Tuple(bool,default=(False,False))) 
    grid_alpha = d_(FloatRange(low=0.0,high=1.0,value=0.5))
    
    multi_axis = d_(Bool(True))
    
    log_mode = d_(Tuple(bool,default=(False,False))) # x,y
    
    
    antialias = d_(Bool(False))
    
    # Set auto range for each axis
    auto_range = d_(Enum(True,False,(True,True),(True,False),(False,True),(False,False)))
    
    # These mean nothing if auto_range is true
    range_x = d_(ContainerList(default=[0,100]))
    range_y = d_(ContainerList(default=[0,100]))
    
    auto_downsample = d_(Bool(False))
    clip_to_view = d_(Bool(False))
    step_mode = d_(Bool(False))
    aspect_locked = d_(Bool(False))
    
    @observe('line_pen','symbol','symbol_size','symbol_pen','symbol_brush',
             'fill_brush','fill_level','multi_axis','title',
             'label_left','label_right','label_top','label_bottom',
             'grid','grid_alpha','log_mode','antialias','auto_range',
             'auto_downsample','clip_to_view','step_mode','aspect_locked',)
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(PlotItem, self)._update_proxy(change)
        
    @observe('range_x','range_y')
    def _update_range(self,change):
        """ Handle updates and changes """
        getattr(self.proxy,'set_%s'%change['name'])(change['value'])

class PlotItem2D(PlotItem):
    x = d_(ContainerList())
    y = d_(ContainerList())
    
    @observe('x','y')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(PlotItem2D, self)._update_proxy(change)

class PlotItem3D(PlotItem2D):
    z = d_(ContainerList())
    
    @observe('z')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(PlotItem3D, self)._update_proxy(change)


class PlotItemArray(PlotItem2D):
    """ Numpy array item """
    x = d_(ForwardInstance(numpy_ndarray))
    y = d_(ForwardInstance(numpy_ndarray))
    
class PlotItemArray3D(PlotItem3D):
    """ Numpy array item """
    type = Enum('line')
    x = d_(ForwardInstance(numpy_ndarray))
    y = d_(ForwardInstance(numpy_ndarray))
    z = d_(ForwardInstance(numpy_ndarray))



class AbstractDataPlotItem(PlotItem):
    @observe('data')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractDataPlotItem, self)._update_proxy(change)

class PlotItemList(AbstractDataPlotItem):
    data = d_(ContainerList())
    
class PlotItemDict(AbstractDataPlotItem):
    data = d_(Dict(default={'x':[],'y':[]}))
    
