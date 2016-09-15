# -*- coding: utf-8 -*-
'''
Created on Aug 24, 2015

@author: jrm
'''
from atom.api import Instance, Property, ForwardInstance
from enaml.core.pattern import Pattern
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_menu import QtMenu
from enaml.qt.qt_widget import QtWidget
from enaml.qt.QtGui import QHeaderView
from enaml.qt.QtCore import QModelIndex

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
    #: Context menu for this group
    menu = Instance(QtMenu)
    
    def _get_items(self):
        return [c for c in self.children() if isinstance(c,AbstractQtWidgetItem)]
    
    #: Internal items
    #: TODO: Is a cached property the right thing to use here??
    #: Why not a list??
    _items = Property(lambda self:self._get_items(),cached=True)
    
    def init_layout(self):
        for child in self.children():
            if isinstance(child, QtMenu):
                self.menu = child
    
    def refresh_style_sheet(self):
        pass # Takes a lot of time
    
    def child_added(self, child):
        super(AbstractQtWidgetItemGroup, self).child_added()
        self.get_member('_items').reset(self)
        
    def child_removed(self, child):
        super(AbstractQtWidgetItemGroup, self).child_removed()
        self.get_member('_items').reset(self)
    
def _abstract_item_view():
    from .qt_abstract_item_view import QtAbstractItemView
    return QtAbstractItemView
    
class AbstractQtWidgetItem(AbstractQtWidgetItemGroup,ProxyAbstractWidgetItem):
    #: Index within the view
    index = Instance(QModelIndex)
    
    #: Delegate widget to display when editing the cell
    #: if the widget is editable
    delegate = Instance(QtWidget)
    
    #: Reference to view
    view = ForwardInstance(_abstract_item_view)
    
    def create_widget(self):
        # View items have no widget!
        for child in self.children():
            if isinstance(child,(Pattern,QtWidget)):
                self.delegate = child
                
    def init_widget(self):
        self._update_index()
    
    def _update_index(self):
        """ Update where this item is within the model"""
        raise NotImplementedError
