# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
from atom.api import (Int, Enum, Bool, observe)
from enaml.core.declarative import d_
from enaml.widgets.control import Control

class AbstractItemView(Control):
    current_row = d_(Int())
    
    selection_mode = d_(Enum('extended','none','multi','single','contiguous'))
    
    selection_behavior = d_(Enum('items','rows','columns'))
    
    scroll_to_bottom = d_(Bool(False))
    
    alternating_row_colors = d_(Bool(False))
    
    @observe('current_row','scroll_to_bottom','alternating_row_colors',
             'selection_mode','selection_behavior')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractItemView, self)._update_proxy(change)