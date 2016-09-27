'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
    Float, Instance, Typed, ForwardTyped, observe, set_default
)
from enaml.widgets.toolkit_object import ToolkitObject
from enaml.core.declarative import d_
from enaml.widgets.control import ProxyControl
from OCC.gp import gp_Pnt

class ProxyBRepPrim(ProxyControl):
    #: A reference to the SpinBox declaration.
    declaration = ForwardTyped(lambda: BRepPrim)
    
    def set_position(self, position):
        raise NotImplementedError

class ProxyBRepBox(ProxyBRepPrim):
    #: A reference to the SpinBox declaration.
    declaration = ForwardTyped(lambda: BRepPrim)
    
    def set_dx(self, dx):
        raise NotImplementedError
    
    def set_dy(self, dy):
        raise NotImplementedError
    
    def set_dz(self, dz):
        raise NotImplementedError

class BRepPrim(ToolkitObject):
    #: Reference to the implementation control
    proxy = Typed(ProxyBRepPrim)
    
    #: Position
    position = d_(Instance(gp_Pnt,(0,0,0)))

class BRepBox(BRepPrim):
    #: x size
    dx = d_(Float(1,strict=False))
    
    #: y size
    dy = d_(Float(1,strict=False))
    
    #: z size
    dz = d_(Float(1,strict=False))
    