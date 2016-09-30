'''
Created on Sep 30, 2016

@author: jrmarti3
'''
from atom.api import (
    Str, Float, Coerced, Typed, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.widgets.control import ProxyControl
from enaml.widgets.toolkit_object import ToolkitObject


from OCC.gp import gp_Pnt,gp_Ax2, gp_Dir
#from OCC.Quantity import Quantity_Color

class ProxyShape(ProxyControl):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Shape)
    
    def set_position(self, position):
        pass
    
    def set_direction(self, direction):
        pass
    
    def set_axis(self, axis):
        raise NotImplementedError
    
    def set_color(self,color):
        pass
    
    def set_transparency(self, alpha):
        pass
    
def coerce_axis(value):
    pos = gp_Pnt(*value[0])
    v = gp_Dir(*value[1])
    return gp_Ax2(pos,v) 

class Shape(ToolkitObject):
    #: Reference to the implementation control
    proxy = Typed(ProxyShape)
    
    #: Color
    color = d_(Str()).tag(view=True,group='Display')#Instance((basestring,Quantity_Color)))
    
    #: Transparency
    transparency = d_(Float(strict=False)).tag(view=True,group='Display')
    
    #: x position
    x = d_(Float(0,strict=False)).tag(view=True,group='Position')
    
    #: y position
    y = d_(Float(0,strict=False)).tag(view=True,group='Position')
    
    #: z position
    z = d_(Float(0,strict=False)).tag(view=True,group='Position')
    
    #: Position
    position = d_(Coerced(gp_Pnt,(0,0,0),coercer=lambda args:gp_Pnt(*args)))
    
    #: Direction
    direction = d_(Coerced(gp_Dir,(0,0,1),coercer=lambda args:gp_Dir(*args)))
    
    #: Axis
    axis = d_(Coerced(gp_Ax2,((0,0,0),(0,0,1)),coercer=coerce_axis))
    
    @observe('x','y','z')
    def _update_position(self, change):
        self.position = gp_Pnt(self.x,self.y,self.z)
    
    @observe('position','direction')
    def _update_axis(self, change):
        self.x,self.y,self.z = self.position.X(),self.position.Y(),self.position.Z()
        self.axis = self._default_axis()
    
    def _default_axis(self):
        return gp_Ax2(self.position,self.direction)
    
    @observe('axis','color')
    def _update_proxy(self, change):
        super(Shape, self)._update_proxy(change)
        self.proxy.update_display(change)