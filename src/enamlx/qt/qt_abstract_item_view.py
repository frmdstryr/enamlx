# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: jrm
'''
from enaml.qt.qt_control import QtControl
from enaml.qt.QtGui import QAbstractItemView

SELECTION_MODES = {
    'extended':QAbstractItemView.ExtendedSelection,
    'single':QAbstractItemView.SingleSelection,
    'contiguous':QAbstractItemView.ContiguousSelection,
    'multi':QAbstractItemView.MultiSelection,
    'none':QAbstractItemView.NoSelection,
}

SELECTION_BEHAVIORS = {
    'items':QAbstractItemView.SelectItems,
    'rows':QAbstractItemView.SelectRows,
    'columns':QAbstractItemView.SelectColumns,
}

class QtAbstractItemView(QtControl):
    
    def init_widget(self):
        super(QtAbstractItemView, self).init_widget()
        
        d = self.declaration
        
        self.set_selection_mode(d.selection_mode)
        self.set_selection_behavior(d.selection_behavior)
        self.set_alternating_row_colors(d.alternating_row_colors)
        
    def _refresh_layout(self):
        self.set_scroll_to_bottom(self.declaration.scroll_to_bottom)
        
    
    def set_selection_mode(self,mode):
        self.widget.setSelectionMode(SELECTION_MODES[mode])
        
    def set_selection_behavior(self,behavior):
        self.widget.setSelectionBehavior(SELECTION_BEHAVIORS[behavior])
        
    def set_scroll_to_bottom(self,scroll):
        if scroll:
            self.widget.scrollToBottom()
            
    def set_alternating_row_colors(self,enabled):
        self.widget.setAlternatingRowColors(enabled)