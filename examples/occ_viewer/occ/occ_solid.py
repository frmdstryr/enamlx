'''
Created on Sep 27, 2016

@author: jrmarti3
'''

from OCC.BRepPrimAPI import (
    BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakePrism,
    BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeWedge, BRepPrimAPI_MakeTorus,
)

from .solid import (
    ProxyBox, ProxyCone, ProxyCylinder,
    ProxyHalfSpace, ProxyPrism, ProxySphere, ProxyWedge,
    ProxyTorus
)

from .occ_shape import OccShape

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
        
    def set_angle(self, a):
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
