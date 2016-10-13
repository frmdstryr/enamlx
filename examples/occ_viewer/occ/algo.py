'''
Created on Sep 28, 2016

@author: jrm
'''

from atom.api import (
    Instance, Typed, ForwardTyped, ContainerList, Enum, Float, observe
)
from enaml.core.declarative import d_

from .shape import ProxyShape, Shape
from enaml.widgets.control import Control

class ProxyOperation(ProxyShape):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Operation)
    
    def set_shape1(self,shape):
        raise NotImplementedError
    
    def set_shape2(self,shape):
        raise NotImplementedError
    
    def set_pave_filler(self,pave_filler):
        raise NotImplementedError
    
    def _do_operation(self,shape1,shape2):
        raise NotImplementedError
    
class ProxyCommon(ProxyOperation):
    declaration = ForwardTyped(lambda: Common)

class ProxyCut(ProxyOperation):
    declaration = ForwardTyped(lambda: Cut)

class ProxyFuse(ProxyOperation):
    declaration = ForwardTyped(lambda: Fuse)

class ProxyFillet(ProxyShape):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Fillet)
    
    def set_radius(self, r):
        raise NotImplementedError
    
    def set_edges(self, edges):
        raise NotImplementedError
    
    def set_shape(self, shape):
        raise NotImplementedError

class ProxyChamfer(ProxyShape):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Chamfer)
    
class ProxyChamferEdge(ProxyShape):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: ChamferEdge)
    
    def set_distance(self, d):
        raise NotImplementedError
    
    def set_distance2(self, d):
        raise NotImplementedError
    
    def set_edge(self, edge):
        raise NotImplementedError
    
    def set_face(self, face):
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
        
