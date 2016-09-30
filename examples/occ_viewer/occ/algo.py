'''
Created on Sep 28, 2016

@author: jrm
'''

#from OCC.BOPAlgo import BOPAlgo_PaveFiller

from atom.api import (
    Instance, Typed, ForwardTyped, observe
)
from enaml.core.declarative import d_

from .shape import ProxyShape, Shape

from OCC.TopoDS import TopoDS_Shape

class ProxyBooleanOperation(ProxyShape):
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
    
    

class BooleanOperation(Shape):
    #: Reference to the implementation control
    proxy = Typed(ProxyBooleanOperation)
    
    shape1 = d_(Instance(TopoDS_Shape))
    
    shape2 = d_(Instance(TopoDS_Shape))
    
    #: Optional pave filler
    pave_filler = d_(Instance(object))#BOPAlgo_PaveFiller))
    
#     @property
#     def color(self):
#         #print self.get_member('color').value
#         for c in self.children:
#             if c.color:
#                 return c.color
#         return None

    @observe('shape1','shape2','pave_filler')
    def _update_proxy(self, change):
        super(BooleanOperation, self)._update_proxy(change)
        self.proxy.update_display(change)
        
class Common(BooleanOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyCommon)

class Cut(BooleanOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyCut)
    
class Fuse(BooleanOperation):
    #: Reference to the implementation control
    proxy = Typed(ProxyFuse)

