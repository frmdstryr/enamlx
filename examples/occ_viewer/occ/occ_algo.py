'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
   Int
)

from enaml.application import timed_call

from .algo import (
    ProxyBooleanOperation, ProxyCommon, ProxyCut, ProxyFuse
)
from .occ_shape import OccShape

from OCC.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse, BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut
)



class OccBooleanOperation(OccShape, ProxyBooleanOperation):
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
        super(OccBooleanOperation, self).child_added(child)
        child.observe('shape',self._queue_update)
        
    def child_remvoed(self, child):
        super(OccBooleanOperation, self).child_removed(child)
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

class OccCommon(OccBooleanOperation,ProxyCommon):
    """ Fuse two shapes along with all child shapes """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Common(*args)
    
class OccCut(OccBooleanOperation,ProxyCut):
    """ Fuse two shapes along with all child shapes """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Cut(*args)

class OccFuse(OccBooleanOperation,ProxyFuse):
    """ Fuse two shapes along with all child shapes """
    
    def _do_operation(self,shape1,shape2):
        d = self.declaration
        args = [shape1,shape2]
        if d.pave_filler:
            args.append(d.pave_filler)
        return BRepAlgoAPI_Fuse(*args)
    
