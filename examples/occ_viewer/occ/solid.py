'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
    Instance, Bool, Float, Typed, ForwardTyped, observe
)
from enaml.core.declarative import d_

from .shape import ProxyShape, Shape

from OCC.TopoDS import TopoDS_Face, TopoDS_Shell, TopoDS_Shape



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

class Box(Shape):
    #: Proxy shape
    proxy = Typed(ProxyBox)
    
    #: x size
    dx = d_(Float(1,strict=False)).tag(view=True)
    
    #: y size
    dy = d_(Float(1,strict=False)).tag(view=True)
    
    #: z size
    dz = d_(Float(1,strict=False)).tag(view=True)
    
    # TODO: Handle other constructors
    
    @observe('dx','dy','dz')
    def _update_proxy(self, change):
        super(Box, self)._update_proxy(change)

class Cone(Shape):
    """ Make a cone of height H radius R1 in the plane z = 0, 
        R2 in the plane Z = H. R1 and R2 may be null."""
    #: Proxy shape
    proxy = Typed(ProxyCone)
    
    #: Radius
    radius = d_(Float(1,strict=False)).tag(view=True)
    
    #: Radius 2 size
    radius2 = d_(Float(0,strict=False)).tag(view=True)
    
    #: Height
    height = d_(Float(1,strict=False)).tag(view=True)
    
    #: Angle
    angle = d_(Float(0,strict=False)).tag(view=True)
    
    @observe('radius','r2','height','angle')
    def _update_proxy(self, change):
        super(Cone, self)._update_proxy(change)
        
class Cylinder(Shape):
    """ Make a cylinder of radius R and length H with angle H.
    
    """
    #: Proxy shape
    proxy = Typed(ProxyCylinder)
    
    #: Radius
    radius = d_(Float(1,strict=False)).tag(view=True)
    
    #: Height
    height = d_(Float(1,strict=False)).tag(view=True)
    
    #: Angle
    angle = d_(Float(0,strict=False)).tag(view=True)
    
    @observe('radius','height','angle')
    def _update_proxy(self, change):
        super(Cylinder, self)._update_proxy(change)
        
class HalfSpace(Shape):
    #: Proxy shape
    proxy = Typed(ProxyHalfSpace)
    
    #: Surface that is either a face or a Shell
    surface = d_(Instance((TopoDS_Face,TopoDS_Shell)))
                 
    @observe('surface')
    def _update_proxy(self, change):
        super(HalfSpace, self)._update_proxy(change)
        
class Prism(Shape):
    #: Proxy shape
    proxy = Typed(ProxyPrism)
    
    #: Shape to build prism from
    shape = d_(Instance(TopoDS_Shape)).tag(view=True)
    
    #: Infinite
    infinite = d_(Bool(False)).tag(view=True)
    
    #: Copy the surface
    copy = d_(Bool(False)).tag(view=True)
    
    #: Attempt to canonize
    canonize = d_(Bool(True)).tag(view=True)
    
    @observe('shape','infinite','copy','canonize')
    def _update_proxy(self, change):
        super(HalfSpace, self)._update_proxy(change)
        
class Sphere(Shape):
    #: Proxy shape
    proxy = Typed(ProxySphere)
    
    #: Radius of sphere
    radius = d_(Float(1,strict=False)).tag(view=True)
    
    #: angle 1
    angle = d_(Float(0,strict=False)).tag(view=True)
    
    #: angle 2
    angle2 = d_(Float(0,strict=False)).tag(view=True)
    
    #: angle 3
    angle3 = d_(Float(0,strict=False)).tag(view=True)
    
    @observe('radius','angle','angle2','angle3')
    def _update_proxy(self, change):
        super(Sphere, self)._update_proxy(change)
        
class Torus(Shape):
    #: Proxy shape
    proxy = Typed(ProxyTorus)
    
    #: Radius of sphere
    radius = d_(Float(1,strict=False)).tag(view=True)
    
    #: Radius 2
    radius2 = d_(Float(0,strict=False)).tag(view=True)
    
    #: angle 1
    angle = d_(Float(0,strict=False)).tag(view=True)
    
    #: angle 2
    angle2 = d_(Float(0,strict=False)).tag(view=True)
    
    @observe('radius','radius2','angle1','angle2')
    def _update_proxy(self, change):
        super(Torus, self)._update_proxy(change)
        
class Wedge(Shape):
    #: Proxy shape
    proxy = Typed(ProxyWedge)
    
    #: x size
    dx = d_(Float(1,strict=False)).tag(view=True)
    
    #: y size
    dy = d_(Float(1,strict=False)).tag(view=True)
    
    #: z size
    dz = d_(Float(1,strict=False)).tag(view=True)
    
    #: z size
    itx = d_(Float(0,strict=False)).tag(view=True)
    
    # TODO: Handle other constructors
    
    @observe('dx','dy','dz','itx')
    def _update_proxy(self, change):
        super(Wedge, self)._update_proxy(change)
        
    