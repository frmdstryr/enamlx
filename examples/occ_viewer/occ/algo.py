'''
Created on Sep 28, 2016

@author: jrm
'''

from atom.api import (
    Instance, ForwardInstance, Typed, ForwardTyped, ContainerList, Enum, Float, Bool, Coerced, observe
)
from enaml.core.declarative import d_

from .shape import ProxyShape, Shape

def WireFactory():
    #: Deferred import of wire
    from .draw import Wire
    return Wire

class ProxyOperation(ProxyShape):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Operation)
    
class ProxyBooleanOperation(ProxyOperation):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: BooleanOperation)
    
    def set_shape1(self,shape):
        raise NotImplementedError
    
    def set_shape2(self,shape):
        raise NotImplementedError
    
    def set_pave_filler(self,pave_filler):
        raise NotImplementedError
    
    def _do_operation(self,shape1,shape2):
        raise NotImplementedError
    
class ProxyCommon(ProxyBooleanOperation):
    declaration = ForwardTyped(lambda: Common)

class ProxyCut(ProxyBooleanOperation):
    declaration = ForwardTyped(lambda: Cut)

class ProxyFuse(ProxyBooleanOperation):
    declaration = ForwardTyped(lambda: Fuse)

class ProxyFillet(ProxyOperation):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Fillet)
    
    def set_radius(self, r):
        raise NotImplementedError
    
    def set_edges(self, edges):
        raise NotImplementedError
    
    def set_shape(self, shape):
        raise NotImplementedError

class ProxyChamfer(ProxyOperation):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Chamfer)
    
    def set_distance(self, d):
        raise NotImplementedError
    
    def set_distance2(self, d):
        raise NotImplementedError
    
    def set_edges(self, edges):
        raise NotImplementedError
    
    def set_faces(self, faces):
        raise NotImplementedError
    
class ProxyOffset(ProxyOperation):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Offset)
    
    def set_offset(self, offset):
        raise NotImplementedError
    
    def set_offset_mode(self, mode):
        raise NotImplementedError
    
    def set_intersection(self, enabled):
        raise NotImplementedError
    
    def set_join_type(self, mode):
        raise NotImplementedError

class ProxyThickSolid(ProxyOffset):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: ThickSolid)
    
    def set_closing_faces(self, faces):
        raise NotImplementedError
    
class ProxyPipe(ProxyOffset):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Pipe)
    
    def set_spline(self, spline):
        raise NotImplementedError
    
    def set_profile(self, profile):
        raise NotImplementedError
    
    def set_fill_mode(self, mode):
        raise NotImplementedError
    
class ProxyAbstractRibSlot(ProxyOperation):
    #: Abstract class 
    
    def set_shape(self, shape):
        raise NotImplementedError
    
    def set_contour(self, contour):
        raise NotImplementedError
    
    def set_plane(self, plane):
        raise NotImplementedError
    
    def set_fuse(self, fuse):
        raise NotImplementedError
    
class ProxyLinearForm(ProxyAbstractRibSlot):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: LinearForm)
    
    def set_direction(self, direction):
        raise NotImplementedError
    
    def set_direction1(self, direction):
        raise NotImplementedError

    def set_modify(self, modify):
        raise NotImplementedError
    
class ProxyRevolutionForm(ProxyAbstractRibSlot):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: RevolutionForm)
    
    def set_height1(self, direction):
        raise NotImplementedError
    
    def set_height2(self, direction):
        raise NotImplementedError
    
    def set_sliding(self, sliding):
        raise NotImplementedError

class ProxyThruSections(ProxyOperation):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: ThruSections)
    
    def set_solid(self, solid):
        raise NotImplementedError
    
    def set_ruled(self, ruled):
        raise NotImplementedError
    
    def set_precision(self, pres3d):
        raise NotImplementedError
    
class ProxyTransform(ProxyOperation):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Transform)
    
    def set_shape(self, shape):
        raise NotImplementedError
    
    def set_mirror(self, axis):
        raise NotImplementedError
    
    def set_rotate(self, rotation):
        raise NotImplementedError
    
    def set_scale(self, scale):
        raise NotImplementedError
    
    def set_translate(self, translation):
        raise NotImplementedError
    
class Operation(Shape):
    #: Reference to the implementation control
    proxy = Typed(ProxyOperation)
    
    def _update_proxy(self, change):
        if change['name']=='axis':
            dx,dy,dz = self.x,self.y,self.z
            if change.get('oldvalue',None):
                old = change['oldvalue'].Location()
                dx -= old.X()
                dy -= old.Y()
                dz -= old.Z()
            for c in self.children:
                if isinstance(c,Shape):
                    c.position = (c.x+dx,c.y+dy,c.z+dz) 
        else:
            super(Operation, self)._update_proxy(change)
        self.proxy.update_display(change)

class BooleanOperation(Operation):
    shape1 = d_(Instance(object))
    
    shape2 = d_(Instance(object))
    
    #: Optional pave filler
    pave_filler = d_(Instance(object))#BOPAlgo_PaveFiller))
    
    @observe('shape1','shape2','pave_filler')
    def _update_proxy(self, change):
        super(BooleanOperation, self)._update_proxy(change)
        
        
class Common(BooleanOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyCommon)

class Cut(BooleanOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyCut)
    
class Fuse(BooleanOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyFuse)
    
class LocalOperation(Operation):
    pass

class Fillet(LocalOperation):
    """ Applies fillet to the first child shape"""
    #: Reference to the implementation control
    proxy = Typed(ProxyFillet)
    
    #: Fillet shape type
    shape = d_(Enum('rational','angular','polynomial')).tag(view=True, group='Fillet')
    
    #: Radius of fillet
    radius = d_(Float(1, strict=False)).tag(view=True, group='Fillet')
    
    #: Edges to apply fillet to
    #: Leave blank to use all edges of the shape 
    edges = d_(ContainerList(object)).tag(view=True, group='Fillet')
    
    @observe('shape','radius','edges')
    def _update_proxy(self, change):
        super(Fillet, self)._update_proxy(change)
        
class Chamfer(LocalOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyChamfer)
    
    #: Distance of chamfer
    distance = d_(Float(1, strict=False)).tag(view=True, group='Chamfer')
    
    #: Second of chamfer (leave 0 if not used)
    distance2 = d_(Float(0, strict=False)).tag(view=True, group='Chamfer')
    
    #: Edges to apply fillet to
    #: Leave blank to use all edges of the shape 
    edges = d_(ContainerList()).tag(view=True, group='Chamfer')
    
    faces = d_(ContainerList()).tag(view=True, group='Chamfer')
    
    @observe('distance','distance2','edges','faces')
    def _update_proxy(self, change):
        super(Chamfer, self)._update_proxy(change)

class Offset(Operation):
    #: Reference to the implementation control
    proxy = Typed(ProxyOffset)
    
    #: Offset
    offset = d_(Float(1,strict=False)).tag(view=True, group='Offset')
    
    #: Offset mode
    offset_mode = d_(Enum('skin','pipe','recto_verso')).tag(view=True, group='Offset')
    
    #: Intersection
    intersection = d_(Bool(False)).tag(view=True, group='Offset')
    
    #: Join type
    join_type = d_(Enum('arc','tangent','intersection')).tag(view=True, group='Offset')
        
    @observe('offset','offset_mode','intersection','join_type')
    def _update_proxy(self, change):
        super(Offset, self)._update_proxy(change)

class ThickSolid(Offset):
    #: Reference to the implementation control
    proxy = Typed(ProxyThickSolid)
    
    #: Closing faces
    closing_faces = d_(ContainerList()).tag(view=True, group='ThickSolid')
    
    @observe('closing_faces')
    def _update_proxy(self, change):
        super(ThickSolid, self)._update_proxy(change)
        
class Pipe(Operation):
    #: Reference to the implementation control
    proxy = Typed(ProxyPipe)
    
    #: Spline to make the pipe along
    spline = d_(Instance(Shape))
    
    #: Profile to make the pipe from
    profile = d_(ForwardInstance(WireFactory))
    
    #: Fill mode
    fill_mode = d_(Enum(None,'corrected_frenet','fixed','frenet','constant_normal','darboux',
                        'guide_ac','guide_plan','guide_ac_contact','guide_plan_contact','discrete_trihedron')).tag(view=True, group='Pipe')
    
    @observe('spline','profile','fill_mode')
    def _update_proxy(self, change):
        super(Pipe, self)._update_proxy(change)


class AbstractRibSlot(Operation):
    #: Base shape
    shape = d_(Instance(Shape))
    
    #: Profile to make the pipe from
    contour = d_(Instance(Shape))
    
    #: Profile to make the pipe from
    plane = d_(Instance(Shape))
    
    #: Fuse (False to remove, True to add)
    fuse = d_(Bool(False)).tag(view=True)

class LinearForm(AbstractRibSlot):
    #: Reference to the implementation control
    proxy = Typed(ProxyLinearForm)
    
    #: Direction
    direction1 = d_(Instance((list,tuple))).tag(view=True)
    
    #: Modify
    modify = d_(Bool(False)).tag(view=True)
    
class RevolutionForm(AbstractRibSlot):
    #: Reference to the implementation control
    proxy = Typed(ProxyRevolutionForm)
    
    #: Height 1
    height1 = d_(Float(1.0,strict=False)).tag(view=True)
    
    #: Height 2
    height2 = d_(Float(1.0,strict=False)).tag(view=True)
    
    #: Sliding
    sliding = d_(Bool(False)).tag(view=True)
    
        
class ThruSections(Operation):
    #: Reference to the implementation control
    proxy = Typed(ProxyThruSections)
    
    #: isSolid is set to true if the construction algorithm is required 
    #: to build a solid or to false if it is required to build a shell (the default value),
    solid = d_(Bool(False)).tag(view=True, group='Through Sections')
    
    #: ruled is set to true if the faces generated between the edges 
    #: of two consecutive wires are ruled surfaces or to false (the default value) 
    #: if they are smoothed out by approximation
    ruled = d_(Bool(False)).tag(view=True, group='Through Sections')
    
    #: pres3d defines the precision criterion used by the approximation algorithm; 
    #: the default value is 1.0e-6. Use AddWire and AddVertex to define 
    #: the successive sections of the shell or solid to be built.
    precision = d_(Float(1e-6)).tag(view=True, group='Through Sections')
    
    @observe('solid','ruled','precision')
    def _update_proxy(self, change):
        super(ThruSections, self)._update_proxy(change)
        
class Transform(Operation):
    #: Reference to the implementation control
    proxy = Typed(ProxyTransform)
    
    #: Shape to transform
    #: if none is given the first child will be used
    shape = d_(Instance(Shape))
    
    #: Mirror
    mirror = d_(Instance((tuple,list)))
    
    #: Scale
    scale = d_(Instance((tuple,list)))
    
    #: Rotation
    rotate = d_(Instance((tuple,list)))
    
    #: Translation
    translate = d_(Instance((tuple,list)))
    
    @observe('shape','mirror','scale','rotate','translate')
    def _update_proxy(self, change):
        super(Transform, self)._update_proxy(change)
        
        