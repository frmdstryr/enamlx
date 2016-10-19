'''
Created on Sep 27, 2016

@author: jrm
'''
from atom.api import (
   Int, Dict
)

from enaml.application import timed_call

from .algo import (
    ProxyOperation, ProxyCommon, ProxyCut, ProxyFuse,
    ProxyFillet, ProxyChamfer, ProxyThickSolid
)
from .occ_shape import OccShape

from OCC.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse, BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut
)
from OCC.BRepFilletAPI import (
    BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
)
from OCC.ChFi3d import ChFi3d_Rational, ChFi3d_QuasiAngular, ChFi3d_Polynomial
from OCC import BRepBuilderAPI
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
from OCC.BRepOffset import BRepOffset_Skin, BRepOffset_Pipe,\
    BRepOffset_RectoVerso
from OCC.GeomAbs import GeomAbs_Arc, GeomAbs_Tangent, GeomAbs_Intersection
from OCC.TopoDS import TopoDS_ListOfShape
from OCC.TopTools import TopTools_ListOfShape


class OccOperation(OccShape, ProxyOperation):
    _update_count = Int(0)
    
    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_shape(self):
        """ Create the toolkit shape for the proxy object.

        This method is called during the top-down pass, just before the
        'init_shape()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        d = self.declaration
        if d.shape1 and d.shape2:
            self.shape = self._do_operation(d.shape1, d.shape2)
        else:
            self.shape = None

    def init_layout(self):
        """ Initialize the layout of the toolkit shape.

        This method is called during the bottom-up pass. This method
        should initialize the layout of the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        for child in self.children():
            self.child_added(child)
        self.update_shape({})
        
    
    def child_added(self, child):
        super(OccOperation, self).child_added(child)
        child.observe('shape',self._queue_update)
        
    def child_removed(self, child):
        super(OccOperation, self).child_removed(child)
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
        
    def update_shape(self,change):
        self.create_shape()
        for c in self.children():
            if self.shape:
                self.shape = self._do_operation(self.shape.Shape(),c.shape.Shape())
            else:
                self.shape = c.shape
    
    def update_display(self,change):
        self.parent().update_display(change)
        
    def set_axis(self, axis):
        self._queue_update({})

class OccCommon(OccOperation,ProxyCommon):
    """ Fuse two shapes along with all child shapes """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Common(*args)
    
class OccCut(OccOperation,ProxyCut):
    """ Fuse two shapes along with all child shapes """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Cut(*args)

class OccFuse(OccOperation,ProxyFuse):
    """ Fuse two shapes along with all child shapes """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Fuse(*args)
    
class OccFillet(OccOperation, ProxyFillet):
    
    shape_types = Dict(default={
        'rational':ChFi3d_Rational, 
        'angular':ChFi3d_QuasiAngular, 
        'polynomial':ChFi3d_Polynomial
    })
    
    def create_shape(self):
        """ Cannot be created until the child shape exists. """
        pass
    
    def update_shape(self, change={}):
        d = self.declaration
        
        #: Get the shape to apply the fillet to
        children = [c for c in self.children()]
        if not children:
            raise ValueError("Fillet must have a child shape to operate on.")
        child = children[0]
        s = child.shape.Shape()
        shape = BRepFilletAPI_MakeFillet(s)#,self.shape_types[d.shape])
        
        edges = d.edges if d.edges else child.topology.edges()
        for edge in edges:
            shape.Add(d.radius, edge)
        #if not shape.HasResult():
        #    raise ValueError("Could not compute fillet, radius possibly too small?")
        self.shape = shape
        
    def set_shape(self, shape):
        self.update_shape()
        
    def set_radius(self, r):
        self.update_shape()
        
    def set_edges(self, edges):
        self.update_shape()
        
        
class OccChamfer(OccOperation, ProxyChamfer):
    
    def create_shape(self):
        """ Cannot be created until the child shape exists. """
        pass
    
    def get_shape(self):
        """ Return shape to apply the chamfer to. """
        for child in self.children():
            return child
    
    def get_edges(self,shape):
        d = self.declaration
        edges = d.edges or shape.topology.edges()
        faces = d.faces or shape.topology.faces()
        return zip(edges,faces)#[c for c in self.children() if isinstance(c,OccChamferEdge)]
    
    def update_shape(self, change={}):
        d = self.declaration
        
        #: Get the shape to apply the fillet to
        s = self.get_shape()
        
        shape = BRepFilletAPI_MakeChamfer(s.shape.Shape())
        
        for edge,face in self.get_edges(s):
            args = [d.distance]
            if d.distance2:
                args.append(d.distance2)
            args.extend([edge,face])
            shape.Add(*args)
                
        self.shape = shape

     
    def set_distance(self, d):
        self.update_shape()
         
    def set_distance2(self, d):
        self.update_shape()
         
    def set_edge(self, edge):
        self.update_shape()
         
    def set_face(self, face):
        self.update_shape()
        
class OccThickSolid(OccOperation, ProxyThickSolid):
    
    offset_modes = Dict(default={
        'skin': BRepOffset_Skin,
        'pipe': BRepOffset_Pipe,
        'recto_verso': BRepOffset_RectoVerso
    })
    
    join_types = Dict(default={
        'arc': GeomAbs_Arc,
        'tangent': GeomAbs_Tangent,
        'intersection': GeomAbs_Intersection,
    })
    
    def create_shape(self):
        """ Cannot be created until the child shape exists. """
        pass
    
    def get_shape(self):
        """ Return shape to apply the chamfer to. """
        for child in self.children():
            return child
        
    def get_faces(self, shape):
        d = self.declaration
        if d.closing_faces:
            return d.closing_faces
        for face in shape.topology.faces():
            return [face]
    
    def update_shape(self, change={}):
        d = self.declaration
        
        #: Get the shape to apply the fillet to
        s = self.get_shape()
        
        faces = TopTools_ListOfShape()
        for f in self.get_faces(s):
            faces.Append(f)
        
        self.shape = BRepOffsetAPI_MakeThickSolid(
            s.shape.Shape(),
            faces,
            d.offset,
            d.tolerance,
            self.offset_modes[d.offset_mode],
            d.intersection,
            False,
            self.join_types[d.join_type]
        )
        
    def set_closing_faces(self, faces):
        self.update_shape()
    
    def set_offset(self, offset):
        self.update_shape()
        
    def set_offset_mode(self, mode):
        self.update_shape()
        
    def set_join_type(self, mode):
        self.update_shape()
        
    def set_intersection(self, enabled):
        self.update_shape()