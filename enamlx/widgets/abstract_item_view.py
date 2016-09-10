# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
from atom.api import (Enum, Bool, Property, ForwardInstance, observe)
from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl

from .abstract_item import AbstractWidgetItemGroup

class ProxyAbstractItemView(ProxyControl):
    declaration = ForwardInstance(lambda: AbstractItemView) 
    
    def set_selection_mode(self,mode):
        pass
    
    def set_selection_behavior(self,behavior):
        pass
    
    def set_scroll_to_bottom(self,scroll_to_bottom):
        pass
    
    def set_alternating_row_colors(self,alternate):
        pass

class AbstractItemView(Control):
    
    #: Selection mode of the view
    selection_mode = d_(Enum('extended','none','multi','single','contiguous'))
    
    #: Selectio behavior of the view
    selection_behavior = d_(Enum('items','rows','columns'))
    
    #: Automatically scroll to bottm when new items are added 
    scroll_to_bottom = d_(Bool(False))
    
    #: Set alternating row colors
    alternating_row_colors = d_(Bool(False))
    
    def _get_items(self):
        return [c for c in self.children if isinstance(c,AbstractWidgetItemGroup)]
    
    #: Cached property listing the row or columns of the table
    _items = Property(_get_items,cached=True)
    
    @observe('current_row','scroll_to_bottom','alternating_row_colors',
             'selection_mode','selection_behavior')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractItemView, self)._update_proxy(change)
        
    def child_added(self, child):
        self.get_member('_items').reset(self)
        
    def child_removed(self, child):
        self.get_member('_items').reset(self)