'''
Created on Sep 30, 2016

@author: jrm
'''
from atom.api import (
   Typed, Int, List
)

from enaml.application import timed_call

from .draw import (
    ProxyPoint, ProxyVertex, ProxyLine, ProxyCircle, ProxyEllipse, 
    ProxyHyperbola, ProxyParabola, ProxyEdge, ProxyWire, 
    ProxySegment, ProxyArc, ProxyPolygon,
)
from .occ_shape import OccShape, OccDependentShape

from OCC.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeVertex, BRepBuilderAPI_Transform, 
    BRepBuilderAPI_MakePolygon
)
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakeOffset
from OCC.gce import gce_MakeLin
from OCC.GC import GC_MakeSegment, GC_MakeArcOfCircle
from OCC.gp import gp_Pnt, gp_Lin, gp_Circ, gp_Elips, gp_Hypr, gp_Parab
from OCC.TopoDS import TopoDS_Vertex, topods

class OccPoint(OccShape, ProxyPoint):
    #: A reference to the toolkit shape created by the proxy.
    shape = Typed(gp_Pnt)
    
    def create_shape(self):
        d = self.declaration
        # Not sure why but we need this
        # to force a sync of position and xyz
        d.position
         
        self.shape = gp_Pnt(d.x,d.y,d.z)
        
    def set_position(self, position):
        self.create_shape()
                
class OccVertex(OccShape, ProxyVertex):
    #: A reference to the toolkit shape created by the proxy.
    shape = Typed(TopoDS_Vertex)
    
    def create_shape(self):
        d = self.declaration
        v = BRepBuilderAPI_MakeVertex(gp_Pnt(d.x,d.y,d.z))
        self.shape = v.Vertex()
        
    def set_x(self, x):
        self.create_shape()
        
    def set_y(self, y):
        self.create_shape()    
        
    def set_z(self, z):
        self.create_shape()
    
class OccEdge(OccShape, ProxyEdge):
    shape = Typed(BRepBuilderAPI_MakeEdge)
    
    def make_edge(self,*args):
        self.shape = BRepBuilderAPI_MakeEdge(*args)
        
class OccLine(OccEdge, ProxyLine):
    
    def create_shape(self):
        pass
    
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
        self.update_shape({})
    
    def update_shape(self,change):
        d = self.declaration
        if len(d.children)==2:
            points = [c.shape for c in self.children()]
            shape = gce_MakeLin(points[0],points[1]).Value()
        else:
            shape = gp_Lin(d.axis)
        self.make_edge(shape)
    
    def child_added(self, child):
        super(OccLine, self).child_added(child)
        if not isinstance(child, (OccPoint, OccVertex)):
            raise TypeError("{} can only have Points or Vertices as children".format(self))
        child.observe('shape',self.update_shape)
        
    def child_removed(self, child):
        super(OccLine, self).child_removed(child)
        child.unobserve('shape',self.update_shape)
        
class OccSegment(OccLine, ProxySegment):
    
    shape = List(BRepBuilderAPI_MakeEdge)
    
    def get_points(self):
        return [c.shape for c in self.children() if isinstance(c,OccPoint)]
    
    def update_shape(self,change):
        d = self.declaration
        points = self.get_points()
        if len(points)>1:
            edges = []
            for i in range(1,len(points)):
                segment = GC_MakeSegment(points[i-1],points[i]).Value()
                edges.append(BRepBuilderAPI_MakeEdge(segment))
            self.shape = edges
            
class OccArc(OccLine, ProxyArc):
    
    def update_shape(self,change):
        d = self.declaration
        if len(d.children)==3:
            points = [c.shape for c in self.children()]
            if not points[0].IsEqual(points[2],d.tolerance):
                arc = GC_MakeArcOfCircle(points[0],points[1],points[2]).Value()
                self.make_edge(arc)
    
class OccCircle(OccEdge, ProxyCircle):
    def create_shape(self):
        d = self.declaration
        self.make_edge(gp_Circ(d.axis,d.radius))
        
    def set_radius(self, r):
        self.create_shape()

class OccEllipse(OccEdge, ProxyEllipse):
    
    def create_shape(self):
        d = self.declaration
        self.make_edge(gp_Elips(d.axis,d.major_radius,d.minor_radius))
        
    def set_major_radius(self, r):
        self.create_shape()
        
    def set_minor_radius(self, r):
        self.create_shape()
        
class OccHyperbola(OccEdge, ProxyHyperbola):
    
    def create_shape(self):
        d = self.declaration
        self.make_edge(gp_Hypr(d.axis,d.major_radius,d.minor_radius))
        
    def set_major_radius(self, r):
        self.create_shape()
        
    def set_minor_radius(self, r):
        self.create_shape()
        
class OccParabola(OccEdge, ProxyParabola):
    
    def create_shape(self):
        d = self.declaration
        self.make_edge(gp_Parab(d.axis,d.focal_length))
        
    def set_focal_length(self, l):
        self.create_shape()
        
class OccPolygon(OccDependentShape, OccEdge, ProxyPolygon):
    
    shape = Typed(BRepBuilderAPI_MakePolygon)
    
    def update_shape(self, change):
        d = self.declaration
        shape = BRepBuilderAPI_MakePolygon()
        for child in self.children():
            if isinstance(child,(OccPoint, OccVertex)):
                shape.Add(child.shape)
        self.shape = shape
        
    def set_closed(self, closed):
        self.update_shape({})
    
class OccWire(OccShape, ProxyWire):
    _update_count = Int(0)
    
    #: Make wire
    shape = Typed(BRepBuilderAPI_MakeWire)
    
    def create_shape(self):
        pass
    
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
        #: Immediate update
        self.update_shape({})
    
    def update_shape(self,change):
        d = self.declaration
        shape = BRepBuilderAPI_MakeWire()
        for c in self.children():
            if hasattr(c.shape,'Wire'):
                #: No conversion needed
                shape.Add(c.shape.Wire())
            elif hasattr(c.shape,'Edge'):
                #: No conversion needed
                shape.Add(c.shape.Edge())
            elif isinstance(c.shape,(list,tuple)):
                #: Assume it's a list of drawn objects...
                for e in c.shape: 
                    shape.Add(e.Edge())
            else:
                #: Attempt to convert the shape into a wire
                shape.Add(topods.Wire(c.shape.Shape()))
                    
        assert shape.IsDone(), 'Edges must be connected'
        self.shape = shape
        
    def child_added(self, child):
        super(OccWire, self).child_added(child)
        child.observe('shape',self._queue_update)
        
    def child_removed(self, child):
        super(OccEdge, self).child_removed(child)
        child.unobserve('shape',self._queue_update)
        
    def _queue_update(self,change=None):
        change = change or {}
        self._update_count +=1
        timed_call(0,self._dequeue_update,change)
    
    def _dequeue_update(self,change):
        # Only update when all changes are done
        self._update_count -=1
        if self._update_count !=0:
            return
        self.update_shape(change)
        