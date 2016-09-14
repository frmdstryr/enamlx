# -*- coding: utf-8 -*-
'''
Created on Aug 24, 2015

@author: jrm
'''
from atom.api import Instance, Property
from enaml.core.pattern import Pattern
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_menu import QtMenu
from enaml.qt.qt_widget import QtWidget
from enaml.qt.QtGui import QAbstractItemView,QHeaderView

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
    _items = Property(_get_items,cached=True)
    
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
    
class AbstractQtWidgetItem(AbstractQtWidgetItemGroup,ProxyAbstractWidgetItem):
    
    #: Delegate widget to display when editing the cell
    #: if the widget is editable
    delegate = Instance(QtWidget)
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child,(Pattern,QtWidget)):
                self.delegate = child
