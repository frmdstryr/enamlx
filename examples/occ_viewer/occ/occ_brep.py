'''
Created on Sep 27, 2016

@author: jrmarti3
'''
from atom.api import (
   Typed
)

from .brep import ProxyShape, ProxyBox, ProxyCone, ProxyCylinder
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeShape
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone,\
    BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakePrism,\
    BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeWedge, BRepPrimAPI_MakeTorus
from occ.brep import ProxyHalfSpace, ProxyPrism, ProxySphere, ProxyWedge,\
    ProxyTorus

class OccShape(ProxyShape):
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
        raise NotImplementedError

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
        pass
    
    def activate_top_down(self):
        """ Activate the proxy for the top-down pass.

        """
        self.create_shape()
        self.init_shape()
        
    def activate_bottom_up(self):
        """ Activate the proxy tree for the bottom-up pass.

        """
        self.init_layout()
        
        
    def set_axis(self, axis):
        self.create_shape()
    

class OccBox(OccShape,ProxyBox):
    
    def create_shape(self):
        d = self.declaration
        self.shape = BRepPrimAPI_MakeBox(d.axis,d.dx,d.dy,d.dz)#.Shape()

    def set_dx(self, dx):
        self.create_shape()
    
    def set_dy(self, dy):
        self.create_shape()
    
    def set_dz(self, dz):
        self.create_shape()

class OccCone(OccShape,ProxyCone):
    
    def create_shape(self):
        d = self.declaration
        args = [d.axis,d.radius,d.radius2,d.height]
        if d.angle:
            args.append(d.angle)
        self.shape = BRepPrimAPI_MakeCone(*args)

    def set_radius(self, r):
        self.create_shape()
    
    def set_radius2(self, r):
        self.create_shape()
    
    def set_height(self, height):
        self.create_shape()
        
class OccCylinder(OccShape,ProxyCylinder):
    
    def create_shape(self):
        d = self.declaration
        args = [d.axis,d.radius,d.height]
        if d.angle:
            args.append(d.angle)
        self.shape = BRepPrimAPI_MakeCylinder(*args)

    def set_radius(self, r):
        self.create_shape()
        
    def set_angle(self, angle):
        self.create_shape()
    
    def set_height(self, height):
        self.create_shape()
        
class OccHalfSpace(OccShape, ProxyHalfSpace):
    
    def create_shape(self):
        d = self.declaration
        self.shape = BRepPrimAPI_MakeHalfSpace(d.surface,d.position)
        
    def set_surface(self, surface):
        self.create_shape()
        
class OccPrism(OccShape, ProxyPrism):
    
    def create_shape(self):
        d = self.declaration
        self.shape = BRepPrimAPI_MakePrism(d.shape,d.direction,
                                           d.infinite,d.copy,d.canonize)
        
    def set_shape(self, shape):
        self.create_shape()
        
    def set_infinite(self, infinite):
        self.create_shape()
        
    def set_copy(self, copy):
        self.create_shape()
        
    def set_canonize(self, canonize):
        self.create_shape()

class OccSphere(OccShape, ProxySphere):
    
    def create_shape(self):
        d = self.declaration
        args = [d.axis,d.radius]
        #: Ugly...
        if d.angle:
            args.append(d.angle)
            if d.angle2:
                args.append(d.angle2)
                if d.angle3:
                    args.append(d.angle3)
        self.shape = BRepPrimAPI_MakeSphere(*args)
        
    def set_radius(self, r):
        self.create_shape()
        
    def set_angle(self, a):
        self.create_shape()
        
    def set_angle2(self, a):
        self.create_shape()
        
    def set_angle3(self, a):
        self.create_shape()

class OccTorus(OccShape, ProxyTorus):
    
    def create_shape(self):
        d = self.declaration
        args = [d.axis,d.radius,d.radius2]
        #: Ugly...
        if d.angle:
            args.append(d.angle)
            if d.angle2:
                args.append(d.angle2)
        self.shape = BRepPrimAPI_MakeTorus(*args)
        
    def set_radius(self, r):
        self.create_shape()
        
    def set_radius2(self, r):
        self.create_shape()
        
    def set_angle(self, a):
        self.create_shape()
        
    def set_angle2(self, a):
        self.create_shape()
        

class OccWedge(OccShape,ProxyWedge):
    
    def create_shape(self):
        d = self.declaration
        self.shape = BRepPrimAPI_MakeWedge(d.axis,d.dx,d.dy,d.dz,d.itx)#.Shape()

    def set_dx(self, dx):
        self.create_shape()
    
    def set_dy(self, dy):
        self.create_shape()
    
    def set_dz(self, dz):
        self.create_shape()
        
    def set_itx(self, itx):
        self.create_shape()
