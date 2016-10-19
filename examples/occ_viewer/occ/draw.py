'''
Created on Sep 27, 2016

@author: jrm
'''
from atom.api import (
    ContainerList, Float, Typed, ForwardTyped, observe
)
from enaml.core.declarative import d_

from .shape import ProxyShape, Shape
from OCC.TopoDS import TopoDS_Edge, TopoDS_Wire


class ProxyPoint(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Point)
    
class ProxyVertex(ProxyShape):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Vertex)

class ProxyEdge(ProxyShape):
    declaration = ForwardTyped(lambda: Edge)

class ProxyLine(ProxyEdge):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Line)

class ProxyCircle(ProxyEdge):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Circle)
    
    def set_radius(self, r):
        raise NotImplementedError
    
class ProxyEllipse(ProxyEdge):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Ellipse)
    
    def set_major_radius(self, r):
        raise NotImplementedError
    
    def set_minor_radius(self, r):
        raise NotImplementedError
    
class ProxyHyperbola(ProxyEdge):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Hyperbola)
    
    def set_major_radius(self, r):
        raise NotImplementedError
    
    def set_minor_radius(self, r):
        raise NotImplementedError
    
class ProxyParabola(ProxyEdge):
    #: A reference to the shape declaration.
    declaration = ForwardTyped(lambda: Parabola)
    
    def set_focal_length(self, l):
        raise NotImplementedError
    
class ProxyWire(ProxyShape):
    declaration = ForwardTyped(lambda: Wire)
    
class Point(Shape):
    """ Creates a point with its 3 cartesian's coordinates : Xp, Yp, Zp. """
    proxy = Typed(ProxyPoint)

class Vertex(Shape):
    proxy = Typed(ProxyVertex)
    
class Edge(Shape):
    proxy = Typed(ProxyEdge)

class Line(Edge):
    """ Creates a line passing through point P and parallel to vector V 
        (P and V are, respectively, the origin and the unit vector 
        of the positioning axis of the line).
    """
    proxy = Typed(ProxyLine)
    
class Circle(Edge):
    """ A2 locates the circle and gives its orientation in 3D space.
        Use point and direction. 
    """
    proxy = Typed(ProxyCircle)
    
    #: Radius of the circle
    radius = d_(Float(1,strict=False)).tag(view=True)
    
    @observe('radius')
    def _update_proxy(self, change):
        super(Circle, self)._update_proxy(change)

class Ellipse(Edge):
    """ A2 locates the circle and gives its orientation in 3D space.
    """
    proxy = Typed(ProxyEllipse)
    
    #: Radius of the ellipse
    major_radius = d_(Float(1,strict=False)).tag(view=True)
    
    #: Minor radius of the ellipse
    minor_radius = d_(Float(1,strict=False)).tag(view=True)
    
    @observe('major_radius','minor_radius')
    def _update_proxy(self, change):
        super(Ellipse, self)._update_proxy(change)
    
class Hyperbola(Edge):
    """ Creates a hyperbola with radii MajorRadius and MinorRadius, positioned in the space by the coordinate system A2 such that:

        - the origin of A2 is the center of the hyperbola,
        - the "X Direction" of A2 defines the major axis of the hyperbola, that is, the major radius MajorRadius is measured along this axis, and
        - the "Y Direction" of A2 defines the minor axis of the hyperbola, that is, the minor radius MinorRadius is measured along this axis. 
        
        Note: This class does not prevent the creation of a hyperbola where:
        - MajorAxis is equal to MinorAxis, or
        - MajorAxis is less than MinorAxis. Exceptions Standard_ConstructionError if MajorAxis or MinorAxis is negative. 
        
        Raises ConstructionError if MajorRadius < 0.0 or MinorRadius < 0.0 Raised if MajorRadius < 0.0 or MinorRadius < 0.0
    """
    proxy = Typed(ProxyHyperbola)
    
    #: Major radius of the hyperbola
    major_radius = d_(Float(1,strict=False)).tag(view=True)
    
    #: Minor radius of the hyperbola
    minor_radius = d_(Float(1,strict=False)).tag(view=True)
    
    @observe('major_radius','minor_radius')
    def _update_proxy(self, change):
        super(Hyperbola, self)._update_proxy(change)
        
class Parabola(Edge):
    """ Creates a parabola with its local coordinate system "A2" and it's focal length "Focal". 
        The XDirection of A2 defines the axis of symmetry of the parabola. 
        The YDirection of A2 is parallel to the directrix of the parabola. 
        The Location point of A2 is the vertex of the parabola 
        Raises ConstructionError if Focal < 0.0 Raised if Focal < 0.0. 
    """
    proxy = Typed(ProxyParabola)
    
    #: Focal length of the parabola
    focal_length = d_(Float(1,strict=False)).tag(view=True)
    
    @observe('focal_length')
    def _update_proxy(self, change):
        super(Parabola, self)._update_proxy(change)     
    
class Wire(Shape):
    proxy = Typed(ProxyWire)
    
    #: Edges used to create this wire 
    edges = d_(ContainerList((TopoDS_Edge,TopoDS_Wire)))
    
    @observe('edges')
    def _update_proxy(self, change):
        super(Wire, self)._update_proxy(change)
    
    