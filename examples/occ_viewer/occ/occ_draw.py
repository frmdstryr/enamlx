'''
Created on Sep 30, 2016

@author: jrm
'''
from atom.api import (
   Typed, Int
)

from .draw import (
    ProxyPoint, ProxyVertex, ProxyLine, ProxyCircle, ProxyEllipse, 
    ProxyHyperbola, ProxyParabola, ProxyEdge, ProxyWire
)

from .occ_shape import OccShape

from OCC.gp import gp_Pnt, gp_Lin, gp_Circ, gp_Elips, gp_Hypr, gp_Parab
from OCC.TopoDS import TopoDS_Vertex
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,\
    BRepBuilderAPI_MakeVertex
from OCC.gce import gce_MakeLin
from enaml.application import timed_call

class OccPoint(OccShape, ProxyPoint):
    #: A reference to the toolkit shape created by the proxy.
    shape = Typed(gp_Pnt)
    
    def create_shape(self):
        d = self.declaration
        self.shape = gp_Pnt(d.x,d.y,d.z)
        
    def set_x(self, x):
        self.create_shape()
        
    def set_y(self, y):
        self.create_shape()    
        
    def set_z(self, z):
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
        self.update_shape()
    
    def update_shape(self,change={}):
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
            raise TypeError("Line can only have Points or Vertices as children")
        child.observe('shape',self.update_shape)
        
    def child_removed(self, child):
        super(OccLine, self).child_removed(child)
        child.unobserve('shape',self.update_shape)

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
    
class OccWire(OccShape, ProxyWire):
    _update_count = Int(0)
    
    shape = Typed(BRepBuilderAPI_MakeWire)
    
    def create_shape(self):
        pass
    
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
        self.update_shape()
    
    def update_shape(self,change={}):
        d = self.declaration
        shape = BRepBuilderAPI_MakeWire()
        for c in self.children():
            shape.Add(c.shape.Edge())
        assert shape.IsDone(), 'Edges must be connected'
        self.shape = shape
        
    def child_added(self, child):
        super(OccWire, self).child_added(child)
        child.observe('shape',self._queue_update)
        
    def child_removed(self, child):
        super(OccEdge, self).child_removed(child)
        child.unobserve('shape',self._queue_update)
        
    def _queue_update(self,change):
        self._update_count +=1
        timed_call(0,self._dequeue_update,change)
    
    def _dequeue_update(self,change):
        # Only update when all changes are done
        self._update_count -=1
        if self._update_count !=0:
            return
        self.update_shape(change)
        