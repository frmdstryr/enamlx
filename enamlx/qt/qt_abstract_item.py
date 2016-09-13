# -*- coding: utf-8 -*-
'''
Created on Aug 24, 2015

@author: jrm
'''
from atom.api import Instance, Property
from enaml.core.pattern import Pattern
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_widget import QtWidget
from enaml.qt.QtGui import QAbstractItemView,QHeaderView

from enaml.qt.qt_menu import QtMenu
from enamlx.widgets.abstract_item import (
    ProxyAbstractWidgetItem,
    ProxyAbstractWidgetItemGroup
)

TEXT_H_ALIGNMENTS = {
    'left':0x01,#Qt.AlignLeft,
    'right':0x02, #Qt.AlignRight,
    'center':0x04, #Qt.AlignHCenter,
    'justify':0x08,#Qt.AlignJustify,
}

TEXT_V_ALIGNMENTS = {
    'top':0x20,#Qt.AlignTop,
    'bottom':0x40,#Qt.AlignBottom,
    'center':0x80,#Qt.AlignVCenter,
}

RESIZE_MODES = {
    'interactive':QHeaderView.Interactive,
    'fixed':QHeaderView.Fixed,
    'stretch':QHeaderView.Stretch,
    'resize_to_contents':QHeaderView.ResizeToContents,
    'custom':QHeaderView.Custom
}

class AbstractQtWidgetItemGroup(QtControl, ProxyAbstractWidgetItemGroup):
    #: Context meu for this group
    menu = Instance(QtMenu)
    
    def _get_items(self):
        return [c for c in self.children() if isinstance(c,AbstractQtWidgetItem)]
    
    _items = Property(_get_items,cached=True)
    
    def init_layout(self):
        for child in self.children():
            if isinstance(child, QtMenu):
                self.menu = child
    
    def refresh_style_sheet(self):
        pass # Takes a lot of time
    
    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_item_activated(self):
        self.declaration.activated()
    
    def on_item_clicked(self):
        self.declaration.clicked()
        self.on_item_checked()
        
    def on_item_double_clicked(self):
        self.declaration.double_clicked()
    
    def on_item_pressed(self):    
        self.declaration.pressed()
        self.on_item_checked()
    
    def on_item_entered(self):    
        self.declaration.entered()
        
    def on_item_changed(self):    
        self.declaration.changed()
        
    def on_item_selection_changed(self):
        for item in self.items():
            item.on_item_selection_changed()
        selected = self.is_selected()
        if selected != self.declaration.selected:
            self.declaration.selected = selected
            self.declaration.selection_changed(selected)
            
    def is_selected(self):
        for item in self.items():
            if item.is_selected():
                return True
        return False
    
    def is_checked(self):
        for item in self.items():
            if item.is_checked():
                return True
        return False
    
        
    def child_added(self, child):
        self.get_member('_items').reset(self)
        
    def child_removed(self, child):
        self.get_member('_items').reset(self)
    
class AbstractQtWidgetItem(AbstractQtWidgetItemGroup,ProxyAbstractWidgetItem):
    #: Reference back to the table
    widget = Instance(QAbstractItemView)
    
    #: Delegate widget to display when editing the cell
    #: if the widget is editable
    delegate = Instance(QtWidget)
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child,(Pattern,QtWidget)):
                self.delegate = child
        
        if self.delegate:
            self.widget = self.parent_widget()
            
    def destroy(self):
        """ WidgetItems are not QtWidgets and cannot be destroyed, 
            they must be cleaned up by the parent view.  """
        self.widget = None # Destroyed by parent
        super(AbstractQtWidgetItem, self).destroy()
    
    
    