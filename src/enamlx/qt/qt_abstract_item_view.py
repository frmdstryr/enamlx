# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: jrm
'''
from atom.api import Instance
from enaml.qt.qt_control import QtControl
from enaml.qt.QtGui import QAbstractItemView
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItemGroup

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
    widget = Instance(QAbstractItemView)
    
    def init_widget(self):
        super(QtAbstractItemView, self).init_widget()
        
        d = self.declaration
        
        self.set_selection_mode(d.selection_mode)
        self.set_selection_behavior(d.selection_behavior)
        self.set_alternating_row_colors(d.alternating_row_colors)
        
        self.init_signals()
        
    def init_signals(self):
        """ Connect signals """
        self.widget.itemActivated.connect(self.on_item_activated)
        self.widget.itemClicked.connect(self.on_item_clicked)
        self.widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.widget.itemEntered.connect(self.on_item_entered)
        self.widget.itemPressed.connect(self.on_item_pressed)
        
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
        
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def on_item_activated(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_activated()
        
    def on_item_clicked(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_clicked()
        
    def on_item_double_clicked(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_double_clicked()
    
    def on_item_pressed(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_pressed()
    
    def on_item_changed(self,item):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_changed()
        
    def on_item_entered(self,item):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_entered()
        
    def on_item_selection_changed(self):    
        """ Delegate event handling to the proxy """
        for child in self.children():
            if isinstance(child,AbstractQtWidgetItemGroup):
                child.on_item_selection_changed()
                                