'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
   Typed
)

from .algo import (
    ProxyBooleanOperation, ProxyCommon, ProxyCut, ProxyFuse
)
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeShape
from OCC.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse, BRepAlgoAPI_Common,
    BRepAlgoAPI_Cut
)

class OccBooleanOperation(ProxyBooleanOperation):
    #: A reference to the toolkit shape created by the proxy.
    shape = Typed(BRepBuilderAPI_MakeShape)

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

    def init_shape(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        pass

    def init_layout(self):
        """ Initialize the layout of the toolkit shape.

        This method is called during the bottom-up pass. This method
        should initialize the layout of the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        for c in self.children():
            if self.shape:
                self.shape = self._do_operation(self.shape.Shape(),c.shape.Shape())
            else:
                self.shape = c.shape
    
    def activate_top_down(self):
        """ Activate the proxy for the top-down pass.

        """
        self.create_shape()
        self.init_shape()
        
    def activate_bottom_up(self):
        """ Activate the proxy tree for the bottom-up pass.

        """
        self.init_layout()
        

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
