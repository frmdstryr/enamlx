'''
Created on Sep 28, 2016

@author: jrm
'''

from atom.api import (
    Typed, ForwardTyped, Str
)
from enaml.core.declarative import d_

from .shape import Shape
from enaml.widgets.control import ProxyControl
from enaml.widgets.toolkit_object import ToolkitObject

class ProxyPart(ProxyControl):
    #: A reference to the Shape declaration.
    declaration = ForwardTyped(lambda: Part)
    
    def update_display(self,change):
        self.parent().update_display(change)
    
class Part(ToolkitObject):
    """ A part is simply a group of shapes """
    #: Reference to the implementation control
    proxy = Typed(ProxyPart)
    
    #: Optional name of the part
    name = d_(Str())
    
    #: Optional description of the part
    description = d_(Str())
    
    @property
    def shapes(self):
        return [child for child in self.children if isinstance(child,Shape)]
    
    

