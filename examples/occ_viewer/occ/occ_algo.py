'''
Created on Sep 27, 2016

@author: jrm
'''
from atom.api import (
   Int, Dict, Instance
)
from enaml.application import timed_call
from .algo import (
    ProxyOperation, ProxyBooleanOperation, ProxyCommon, ProxyCut, ProxyFuse,
    ProxyFillet, ProxyChamfer, ProxyOffset, ProxyThickSolid, 
    ProxyPipe, ProxyThruSections, ProxyTransform, 
)
from .occ_shape import OccShape, OccDependentShape
from OCC.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse, BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut
)
from OCC.BRepBuilderAPI import (
    BRepBuilderAPI_Transform, BRepBuilderAPI_MakeWire
)
from OCC.BRepFilletAPI import (
    BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
)
from OCC.BRepOffsetAPI import (
    BRepOffsetAPI_MakeOffset, BRepOffsetAPI_MakeOffsetShape, 
    BRepOffsetAPI_MakeThickSolid, BRepOffsetAPI_MakePipe,
    BRepOffsetAPI_ThruSections
)
from OCC.BRepOffset import (
    BRepOffset_Skin, BRepOffset_Pipe,
    BRepOffset_RectoVerso
)
from OCC.ChFi3d import (
    ChFi3d_Rational, ChFi3d_QuasiAngular, ChFi3d_Polynomial
)
from OCC.GeomAbs import (
    GeomAbs_Arc, GeomAbs_Tangent, GeomAbs_Intersection
)
from OCC.GeomFill import (
    GeomFill_IsCorrectedFrenet, GeomFill_IsFixed,
    GeomFill_IsFrenet, GeomFill_IsConstantNormal, GeomFill_IsDarboux,
    GeomFill_IsGuideAC, GeomFill_IsGuidePlan, 
    GeomFill_IsGuideACWithContact,GeomFill_IsGuidePlanWithContact, 
    GeomFill_IsDiscreteTrihedron
)
from OCC.gp import (
    gp_Trsf, gp_Vec, gp_Pnt, gp_Ax1, gp_Dir
)
from OCC.TopTools import TopTools_ListOfShape

class OccOperation(OccDependentShape, ProxyOperation):
    """ Operation is a dependent shape that uses queuing to only 
        perform the operation once all changes have settled because
        in general these operations are expensive.
    """
    _update_count = Int(0)
    
    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def _queue_update(self,change):
        """ Schedule an update to be performed in the next available cycle.
            This should be used for expensive operations as opposed to an
            immediate update with update_shape.
        
        """
        self._update_count +=1
        timed_call(0,self._dequeue_update,change)
    
    def _dequeue_update(self,change):
        """ Only update when all changes are done """
        self._update_count -=1
        if self._update_count !=0:
            return
        self.update_shape(change)
    
    def set_direction(self, direction):
        self._queue_update({})
    
    def set_axis(self, axis):
        self._queue_update({})
        
class OccBooleanOperation(OccOperation,ProxyBooleanOperation):
    
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
    
    def update_shape(self,change):
        self.create_shape()
        for c in self.children():
            if self.shape:
                self.shape = self._do_operation(self.shape.Shape(),c.shape.Shape())
            else:
                self.shape = c.shape

class OccCommon(OccBooleanOperation,ProxyCommon):
    """ Common of all the child shapes together. """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Common(*args)
    
class OccCut(OccBooleanOperation,ProxyCut):
    """ Cut all the child shapes from the first shape. """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Cut(*args)

class OccFuse(OccBooleanOperation,ProxyFuse):
    """ Fuse all the child shapes together. """
    
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
        self._queue_update({})
        
    def set_radius(self, r):
        self._queue_update({})
        
    def set_edges(self, edges):
        self._queue_update({})
        
        
class OccChamfer(OccOperation, ProxyChamfer):
    
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
        self._queue_update({})
         
    def set_distance2(self, d):
        self._queue_update({})
         
    def set_edge(self, edge):
        self._queue_update({})
         
    def set_face(self, face):
        self._queue_update({})

class OccOffset(OccOperation, ProxyOffset):
    
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
    
    def get_shape(self):
        """ Return shape to apply the chamfer to. """
        for child in self.children():
            return child
        
    def update_shape(self, change={}):
        d = self.declaration
        
        #: Get the shape to apply the fillet to
        s = self.get_shape()
        
        if isinstance(s.shape,BRepBuilderAPI_MakeWire):
            shape = BRepOffsetAPI_MakeOffset(
                s.shape.Wire(),
                self.join_types[d.join_type]
            )
            shape.Perform(d.offset)
            self.shape = shape
        else:
            self.shape = BRepOffsetAPI_MakeOffsetShape(
                s.shape.Shape(),
                d.offset,
                d.tolerance,
                self.offset_modes[d.offset_mode],
                d.intersection,
                False,
                self.join_types[d.join_type]
            )
        
    def set_offset(self, offset):
        self._queue_update({})
        
    def set_offset_mode(self, mode):
        self._queue_update({})
        
    def set_join_type(self, mode):
        self._queue_update({})
        
    def set_intersection(self, enabled):
        self._queue_update({})

class OccThickSolid(OccOffset, ProxyThickSolid):
    
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
        if faces.IsEmpty():
            return
        
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
        self._queue_update({})
    

class OccPipe(OccOperation, ProxyPipe):
    
    fill_modes = Dict(default={
        'corrected_frenet': GeomFill_IsCorrectedFrenet,
        'fixed': GeomFill_IsFixed,
        'frenet': GeomFill_IsFrenet,
        'constant_normal': GeomFill_IsConstantNormal,
        'darboux': GeomFill_IsDarboux,
        'guide_ac': GeomFill_IsGuideAC,
        'guide_plan': GeomFill_IsGuidePlan,
        'guide_ac_contact': GeomFill_IsGuideACWithContact,
        'guide_plan_contact': GeomFill_IsGuidePlanWithContact,
        'discrete_trihedron': GeomFill_IsDiscreteTrihedron
    })
    
    def update_shape(self, change):
        d = self.declaration
        
        i = 0
        shapes = [c for c in self.children() if isinstance(c,OccShape)]
        
        if d.spline:
            spline = d.spline
        else:
            spline = shapes[i]
            i+=1
             
        profile = d.profile or shapes[i]
        
        if d.fill_mode:
            self.shape = BRepOffsetAPI_MakePipe(spline.shape.Wire(),
                                                profile.shape.Shape(),
                                                self.fill_modes[d.fill_mode])
        else:
            self.shape = BRepOffsetAPI_MakePipe(spline.shape.Wire(),
                                                profile.shape.Shape())
    
    def set_spline(self, spline):
        self._queue_update({})
        
    def set_profile(self, profile):
        self._queue_update({})
        
    def set_fill_mode(self, mode):
        self._queue_update({})


class OccThruSections(OccOperation, ProxyThruSections):

    def update_shape(self, change):
        from .occ_draw import OccVertex, OccWire
        
        d = self.declaration
        
        shape = BRepOffsetAPI_ThruSections(d.solid,
                                           d.ruled,
                                           d.precision)
        
        #: TODO: Support Smoothing, Max degree, par type, etc...
        
        for child in self.children():
            if isinstance(child,OccVertex):
                shape.AddVertex(child.shape.Vertex())
            elif isinstance(child,OccWire):
                shape.AddWire(child.shape.Wire())
            #: TODO: Handle transform???
        
        #: Set the shape
        self.shape = shape
        
    def set_solid(self, solid):
        self._queue_update({})
        
    def set_ruled(self, ruled):
        self._queue_update({})
        
    def set_precision(self, pres3d):
        self._queue_update({})

class OccTransform(OccOperation, ProxyTransform):
    
    _old_shape = Instance(OccShape)
    
    def init_shape(self):
        d = self.declaration
        if d.shape:
            #: Make sure we bind the observer
            self.set_shape(d.shape)
    
    def get_shape(self):
        """ Return shape to apply the transform to. """
        for child in self.children():
            return child
        
    def get_transform(self):
        d = self.declaration
        t = gp_Trsf()
        #: TODO: Order matters... how to configure it???
        if d.mirror:
            try:
                p,v = d.mirror
            except ValueError:
                raise ValueError("You must specify a tuple containing a (point,direction)")
            t.SetMirror(gp_Ax1(gp_Pnt(*p),
                               gp_Dir(*v)))
        if d.scale:
            try:
                p,s = d.scale
            except ValueError:
                raise ValueError("You must specify a tuple containing a (point,scale)")
            t.SetScale(gp_Pnt(*p),s)
        
        if d.translate:
            t.SetTranslation(gp_Vec(*d.translate))
        
        if d.rotate:
            try:
                p,v,a = d.rotate
            except ValueError:
                raise ValueError("You must specify a tuple containing a (point,direction,angle)")
            t.SetRotation(gp_Ax1(gp_Pnt(*p),
                               gp_Dir(*v)),a)
            
        return t
    
    def update_shape(self, change):
        d = self.declaration
        
        #: Get the shape to apply the tranform to
        if d.shape:
            make_copy = True
            s = d.shape.proxy
        else:
            # Use the first child
            make_copy = False
            s = self.get_shape()
        t = self.get_transform()
        self.shape = BRepBuilderAPI_Transform(s.shape.Shape(),
                                         t,
                                         make_copy)

    def set_shape(self, shape):
        if self._old_shape:
            self._old_shape.unobserve('shape',self._queue_update)
        self._old_shape = shape.proxy
        self._old_shape.observe('shape',self._queue_update)
        
    def set_translate(self, translation):
        self._queue_update({})
        
    def set_rotate(self, rotation):
        self._queue_update({})
        
    def set_scale(self,scale):
        self._queue_update({})
        
    def set_mirror(self, axis):
        self._queue_update({})
