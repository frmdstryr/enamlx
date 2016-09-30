'''
Created on Sep 30, 2016

@author: jrmarti3
'''
from atom.api import (
   Typed, observe
)

from .shape import ProxyShape

from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeShape


class OccShape(ProxyShape):
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
        raise NotImplementedError

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
    
    @observe('shape')    
    def update_display(self,change):
        self.parent().update_display(change)
        
    def set_axis(self, axis):
        self.create_shape()
    