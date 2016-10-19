'''
Created on Sep 30, 2016

@author: jrm
'''
from atom.api import (
   Typed, observe
)

from .part import ProxyPart
from .occ_shape import OccShape

class OccPart(ProxyPart):
    
    @property
    def shapes(self):
        return [child for child in self.children() if isinstance(child,OccShape)]

