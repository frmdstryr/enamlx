'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
    Float, Instance, Typed, ForwardTyped, observe, set_default
)
from enaml.widgets.toolkit_object import ProxyToolkitObject

from .brep import ProxyBRepPrim,ProxyBRepBox
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeShape
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox

class OccBRepPrim(ProxyBRepPrim):
    #: A reference to the toolkit shape created by the proxy.
    shape = Typed(BRepBuilderAPI_MakeShape)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_shape(self):
        """ Create the toolkit shape for the proxy object.

        This method is called during the top-down pass, just before the
        'init_shape()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        self.shape = BRepBuilderAPI_MakeShape()

    def init_shape(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        pass

    def init_layout(self):
        """ Initialize the layout of the toolkit shape.

        This method is called during the bottom-up pass. This method
        should initialize the layout of the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        pass
    
    def activate_top_down(self):
        """ Activate the proxy for the top-down pass.

        """
        self.create_shape()
        self.init_shape()
        
    def activate_bottom_up(self):
        """ Activate the proxy tree for the bottom-up pass.

        """
        self.init_layout()
        
        
    def set_position(self, position):
        self.create_shape()
    
    def set_axis(self, axis):
        self.create_shape()
    

class OccBRepBox(OccBRepPrim,ProxyBRepBox):
    
    def create_shape(self):
        d = self.declaration
        self.shape = BRepPrimAPI_MakeBox(d.position,d.dx,d.dy,d.dz)#.Shape()

    def set_dx(self, dx):
        self.create_shape()
    
    def set_dy(self, dy):
        self.create_shape()
    
    def set_dz(self, dz):
        self.create_shape()
        
    