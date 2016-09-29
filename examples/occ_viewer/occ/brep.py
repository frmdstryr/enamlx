'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
    Instance, Bool, Float, Coerced, Typed, ForwardTyped, observe
)
from enaml.widgets.toolkit_object import ToolkitObject
from enaml.core.declarative import d_
from enaml.widgets.control import ProxyControl
from OCC.gp import gp_Pnt,gp_Ax2, gp_Dir
from OCC.TopoDS import TopoDS_Face, TopoDS_Shell, TopoDS_Shape
from OCC.Quantity import Quantity_Color

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

class ProxyBox(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Box)
    
    def set_dx(self, dx):
        raise NotImplementedError
    
    def set_dy(self, dy):
        raise NotImplementedError
    
    def set_dz(self, dz):
        raise NotImplementedError
    
class ProxyCone(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Cone)
    
    def set_radius(self, r):
        raise NotImplementedError
    
    def set_radius2(self, r):
        raise NotImplementedError
    
    def set_height(self, height):
        raise NotImplementedError
    
    def set_angle(self, angle):
        raise NotImplementedError
    
class ProxyCylinder(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Cylinder)
    
    def set_radius(self, r):
        raise NotImplementedError
    
    def set_height(self, height):
        raise NotImplementedError
    
    def set_angle(self, angle):
        raise NotImplementedError
    
class ProxyHalfSpace(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: HalfSpace)
    
    def set_surface(self, surface):
        raise NotImplementedError
    
class ProxyPrism(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Prism)
    
    def set_shape(self, surface):
        raise NotImplementedError
    
    def set_infinite(self, infinite):
        raise NotImplementedError
    
    def set_copy(self, copy):
        raise NotImplementedError
    
    def set_canonize(self, canonize):
        raise NotImplementedError

class ProxySphere(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Sphere)
    
    def set_radius(self, r):
        raise NotImplementedError
    
    def set_angle(self, a):
        raise NotImplementedError
    
    def set_angle2(self, a):
        raise NotImplementedError
    
    def set_angle3(self, a):
        raise NotImplementedError
    
class ProxyTorus(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Torus)
    
    def set_radius(self, r):
        raise NotImplementedError
    
    def set_radius2(self, r):
        raise NotImplementedError
    
    def set_angle(self, a):
        raise NotImplementedError
    
    def set_angle2(self, a):
        raise NotImplementedError
    
class ProxyWedge(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Wedge)
    
    def set_dx(self, dx):
        raise NotImplementedError
    
    def set_dy(self, dy):
        raise NotImplementedError
    
    def set_dz(self, dz):
        raise NotImplementedError
    
    def set_itx(self, itx):
        raise NotImplementedError

def coerce_axis(value):
    pos = gp_Pnt(*value[0])
    v = gp_Dir(*value[1])
    return gp_Ax2(pos,v) 

class Shape(ToolkitObject):
    #: Reference to the implementation control
    proxy = Typed(ProxyShape)
    
    #: Color
    color = d_(Instance((basestring,Quantity_Color)))
    
    #: Position
    position = d_(Coerced(gp_Pnt,(0,0,0),coercer=lambda args:gp_Pnt(*args)))
    
    #: Direction
    direction = d_(Coerced(gp_Dir,(0,0,1),coercer=lambda args:gp_Dir(*args)))
    
    #: Axis
    axis = d_(Coerced(gp_Ax2,((0,0,0),(0,0,1)),coercer=coerce_axis))
    
    @observe('position','direction')
    def _update_axis(self, change):
        self.axis = self._default_axis()
        
    def _default_axis(self):
        return gp_Ax2(self.position,self.direction)
    
    @observe('axis','color')
    def _update_proxy(self, change):
        super(Shape, self)._update_proxy(change)

class Box(Shape):
    #: x size
    dx = d_(Float(1,strict=False))
    
    #: y size
    dy = d_(Float(1,strict=False))
    
    #: z size
    dz = d_(Float(1,strict=False))
    
    # TODO: Handle other constructors
    
    @observe('dx','dy','dz')
    def _update_proxy(self, change):
        super(Box, self)._update_proxy(change)

class Cone(Shape):
    """ Make a cone of height H radius R1 in the plane z = 0, 
        R2 in the plane Z = H. R1 and R2 may be null."""
    #: Radius
    radius = d_(Float(1,strict=False))
    
    #: Radius 2 size
    radius2 = d_(Float(0,strict=False))
    
    #: Height
    height = d_(Float(1,strict=False))
    
    #: Angle
    angle = d_(Float(0,strict=False))
    
    @observe('radius','r2','height','angle')
    def _update_proxy(self, change):
        super(Cone, self)._update_proxy(change)
        
class Cylinder(Shape):
    """ Make a cylinder of radius R and length H with angle H.
    
    """
    #: Radius
    radius = d_(Float(1,strict=False))
    
    #: Height
    height = d_(Float(1,strict=False))
    
    #: Angle
    angle = d_(Float(0,strict=False))
    
    @observe('radius','height','angle')
    def _update_proxy(self, change):
        super(Cylinder, self)._update_proxy(change)
        
class HalfSpace(Shape):
    #: Surface that is either a face or a Shell
    surface = d_(Instance((TopoDS_Face,TopoDS_Shell)))
                 
    @observe('surface')
    def _update_proxy(self, change):
        super(HalfSpace, self)._update_proxy(change)
        
class Prism(Shape):
    #: Shape to build prism from
    shape = d_(Instance(TopoDS_Shape))
    
    #: Infinite
    infinite = d_(Bool(False))
    
    #: Copy the surface
    copy = d_(Bool(False))
    
    #: Attempt to canonize
    canonize = d_(Bool(True))
    
    @observe('shape','infinite','copy','canonize')
    def _update_proxy(self, change):
        super(HalfSpace, self)._update_proxy(change)
        
class Sphere(Shape):
    #: Radius of sphere
    radius = d_(Float(1,strict=False))
    
    #: angle 1
    angle = d_(Float(0,strict=False))
    
    #: angle 2
    angle2 = d_(Float(0,strict=False))
    
    #: angle 3
    angle3 = d_(Float(0,strict=False))
    
    @observe('radius','angle','angle2','angle3')
    def _update_proxy(self, change):
        super(Sphere, self)._update_proxy(change)
        
class Torus(Shape):
    #: Radius of sphere
    radius = d_(Float(1,strict=False))
    
    #: Radius 2
    radius2 = d_(Float(0,strict=False))
    
    #: angle 1
    angle = d_(Float(0,strict=False))
    
    #: angle 2
    angle2 = d_(Float(0,strict=False))
    
    @observe('radius','radius2','angle1','angle2')
    def _update_proxy(self, change):
        super(Torus, self)._update_proxy(change)
        
class Wedge(Shape):
    #: x size
    dx = d_(Float(1,strict=False))
    
    #: y size
    dy = d_(Float(1,strict=False))
    
    #: z size
    dz = d_(Float(1,strict=False))
    
    #: z size
    itx = d_(Float(0,strict=False))
    
    # TODO: Handle other constructors
    
    @observe('dx','dy','dz','itx')
    def _update_proxy(self, change):
        super(Wedge, self)._update_proxy(change)
    