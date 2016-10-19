'''
Created on Sep 30, 2016

@author: jrm
'''
from atom.api import (
    Instance, Bool, Str, Float, Property, Coerced, Typed, ForwardTyped, observe
)

from enaml.core.declarative import d_
from enaml.widgets.control import ProxyControl
from enaml.widgets.toolkit_object import ToolkitObject

#: TODO: This breaks the proxy pattern
from OCC.gp import gp_Pnt,gp_Ax2, gp_Dir
from OCC.TopoDS import TopoDS_Face, TopoDS_Shell, TopoDS_Shape

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

class Shape(ToolkitObject):
    #: Reference to the implementation control
    proxy = Typed(ProxyShape)
    
    #: Tolerance
    tolerance = d_(Float(10**-6,strict=False))
    
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
    
    
    def _get_edges(self):
        topo = self.proxy.topology
        if not topo:
            return []
        return [e for e in topo.edges()]
    
    #: Edges of this shape
    shape_edges = Property(lambda self:self._get_edges(),cached=True)
    
    def _get_faces(self):
        topo = self.proxy.topology
        if not topo:
            return []
        return [e for e in topo.faces()]
    
    #: Faces of this shape
    shape_faces = Property(lambda self:self._get_faces(),cached=True)
    
    @observe('x','y','z')
    def _update_position(self, change):
        """ Keep position in sync with x,y,z """
        self.position = gp_Pnt(self.x,self.y,self.z)
        
    @observe('position')
    def _update_xyz(self, change):
        """ Keep x,y,z in sync with position """
        self.x,self.y,self.z = self.position.X(),self.position.Y(),self.position.Z()
    
    @observe('position','direction')
    def _update_axis(self, change):
        """ Keep axis in sync with position and direction """
        axis = self._default_axis()
        if (not self.axis.Location().IsEqual(axis.Location(),self.tolerance) or 
            not self.axis.Direction().IsEqual(self.axis.Direction(),self.tolerance)):
            self.axis = axis
    
    @observe('axis')
    def _update_state(self, change):
        """ Keep position and direction in sync with axis """
        self.position = self.axis.Location()
        self.direction = self.axis.Direction()
    
    def _default_axis(self):
        return gp_Ax2(self.position,self.direction)
    
    @observe('axis','color','transparency')
    def _update_proxy(self, change):
        super(Shape, self)._update_proxy(change)
        self.proxy.update_display(change)
    
    @observe('proxy.shape')
    def _update_topo(self,change):
        self.get_member('shape_edges').reset(self)
        self.get_member('shape_faces').reset(self)
        
    
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
        
    