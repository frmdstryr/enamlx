# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
from atom.api import (
    ContainerList, Int, Enum, Bool, Property, ForwardInstance, observe, set_default
)
from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl

from .abstract_item import AbstractWidgetItemGroup

class ProxyAbstractItemView(ProxyControl):
    declaration = ForwardInstance(lambda: AbstractItemView)
    
    def set_items(self,items):
        pass 
    
    def set_selection_mode(self,mode):
        pass
    
    def set_selection_behavior(self,behavior):
        pass
    
    def set_scroll_to_bottom(self,scroll_to_bottom):
        pass
    
    def set_alternating_row_colors(self,alternate):
        pass
    
    def set_cell_padding(self,padding):
        pass
    
    def set_auto_resize(self,enabled):
        pass
        
    def set_resize_mode(self,mode):
        pass
    
    def set_show_grid(self,show):
        pass
    
    def set_word_wrap(self,enabled):
        pass
    
    def set_show_vertical_header(self,visible):
        pass
    
    def set_vertical_headers(self,headers):
        pass
    
    def set_vertical_stretch(self,stretch):
        pass
    
    def set_vertical_minimum_section_size(self,size):
        pass
    
    def set_show_horizontal_header(self,visible):
        pass
    
    def set_horizontal_headers(self,headers):
        pass
    
    def set_horizontal_stretch(self,stretch):
        pass
    
    def set_horizontal_minimum_section_size(self,size):
        pass
    
    def set_sortable(self,sortable):
        pass
    
    def set_visible_row(self,row):
        pass
    
    def set_visible_column(self,column):
        pass 

class AbstractItemView(Control):
    
    #: Table should expand by default
    hug_width = set_default('ignore')
    
    #: Table should expand by default
    hug_height = set_default('ignore')
    
    #: The items to display in the view
    items = d_(ContainerList(default=[]))
    
    #: Selection mode of the view
    selection_mode = d_(Enum('extended','none','multi','single','contiguous'))
    
    #: Selectio behavior of the view
    selection_behavior = d_(Enum('items','rows','columns'))
    
    #: Automatically scroll to bottm when new items are added 
    scroll_to_bottom = d_(Bool(False))
    
    #: Set alternating row colors
    alternating_row_colors = d_(Bool(False))
    
    #: Cell padding
    cell_padding = d_(Int(0))
    
    #: Automatically resize columns to fit contents
    auto_resize = d_(Bool(True))
    
    #: Resize mode of columns and rows
    resize_mode = d_(Enum('interactive','fixed','stretch','resize_to_contents','custom'))
    
    #: Show grid of cells
    show_grid = d_(Bool(True))
    
    #: Word wrap
    word_wrap = d_(Bool(False))
    
    #: Show vertical header bar
    show_vertical_header = d_(Bool(True))
    
    #: Row headers 
    vertical_headers = d_(ContainerList(basestring))
    
    #: Stretch last row
    vertical_stretch = d_(Bool(False))
    
    #: Minimum row size
    vertical_minimum_section_size = d_(Int(0))
    
    #: Show horizontal hearder bar
    show_horizontal_header = d_(Bool(True))
    
    #: Column headers
    horizontal_headers = d_(ContainerList(basestring))
    
    #: Stretch last column
    horizontal_stretch = d_(Bool(False))
    
    #: Minimum column size
    horizontal_minimum_section_size = d_(Int(0))
    
    #: Table is sortable
    sortable = d_(Bool(True))
    
    #: Current row index
    current_row = d_(Int(0))
    
    #: Current column index
    current_column = d_(Int(0))
    
    #: First visible row
    visible_row = d_(Int(0))
    
    #: Number of rows visible
    visible_rows = d_(Int(100),writable=False)
    
    #: First visible column
    visible_column = d_(Int(0))
    
    #: Number of columns visible
    visible_columns = d_(Int(1),writable=False)
    
    def _get_items(self):
        return [c for c in self.children if isinstance(c,AbstractWidgetItemGroup)]
    
    #: Cached property listing the row or columns of the table
    _items = Property(_get_items,cached=True)
    
    @observe('items','scroll_to_bottom','alternating_row_colors',
             'selection_mode','selection_behavior','cell_padding',
             'auto_resize','resize_mode','show_grid','word_wrap',
             'show_horizontal_header','horizontal_headers','horizontal_stretch',
             'show_vertical_header','vertical_header','vertical_stretch',
             'visible_row','visible_column')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractItemView, self)._update_proxy(change)
        
    def child_added(self, child):
        """ Reset the item cache when a child is added """
        super(AbstractItemView, self).child_added(child)
        self.get_member('_items').reset(self)
        
    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        super(AbstractItemView, self).child_removed(child)
        self.get_member('_items').reset(self)
