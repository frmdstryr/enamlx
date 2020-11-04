# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 24, 2015
"""
from atom.api import (
    Int, Enum, Bool, Str, Typed, 
    Coerced, Event, Property, ForwardInstance, observe
)
from enaml.icon import Icon
from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl
from enaml.layout.geometry import Size


class ProxyAbstractWidgetItemGroup(ProxyControl):
    #: Reference to the declaration
    declaration = ForwardInstance(lambda: AbstractWidgetItemGroup)
    
    def set_selectable(self, selectable):
        pass


class ProxyAbstractWidgetItem(ProxyControl):
    #: Reference to the declaration
    declaration = ForwardInstance(lambda: AbstractWidgetItem)
    
    def set_row(self, row):
        pass
    
    def set_column(self, column):
        pass
    
    def set_text(self, text):
        pass
    
    def set_text_alignment(self, text_alignment):
        pass
    
    def set_icon(self, icon):
        pass
    
    def set_icon_size(self, size):
        pass
    
    def set_editable(self, editable):
        pass
    
    def set_checkable(self, checkable):
        pass


class AbstractWidgetItemGroup(Control):
    
    #: Triggered when clicked
    clicked = d_(Event(), writable=False)
    
    #: Triggered when double clicked
    double_clicked = d_(Event(), writable=False)
    
    #: Triggered when the row, column, or item is entered
    entered = d_(Event(), writable=False)
    
    #: Triggered when the row, column, or item is pressed
    pressed = d_(Event(), writable=False)
    
    #: Triggered when the row, column, or item's selection changes
    selection_changed = d_(Event(bool), writable=False)
    
    def _get_items(self):
        return [c for c in self.children if isinstance(c, AbstractWidgetItem)]
    
    #: Internal item reference
    _items = Property(lambda self: self._get_items(), cached=True)
        
    def child_added(self, child):
        """ Reset the item cache when a child is added """
        super(AbstractWidgetItemGroup, self).child_added(child)
        self.get_member('_items').reset(self)
        
    def child_removed(self, child):
        """ Reset the item cache when a child is removed """
        super(AbstractWidgetItemGroup, self).child_removed(child)
        self.get_member('_items').reset(self)


class AbstractWidgetItem(AbstractWidgetItemGroup):
    """ Item to be shared between table views and tree views """
    
    #: Model index or row within the view
    row = d_(Int(), writable=False)
    
    #: Column within the view
    column = d_(Int(), writable=False)
    
    #: Text to display within the cell
    text = d_(Str())
    
    #: Text alignment within the cell
    text_alignment = d_(Enum(*[(h, v)
                               for h in ('left', 'right', 'center', 'justify')
                               for v in ('center', 'top', 'bottom')]))
    
    #: Icon to display in the cell
    icon = d_(Typed(Icon))
    
    #: The size to use for the icon. The default is an invalid size
    #: and indicates that an appropriate default should be used.
    icon_size = d_(Coerced(Size, (-1, -1)))
    
    #: Whether the item or group can be selected
    selectable = d_(Bool(True))
    
    #: Selection state of the item or group
    selected = d_(Bool())
    
    #: Whether the item or group can be checked
    checkable = d_(Bool())
    
    #: Checked state of the item or group
    checked = d_(Bool())
    
    #: Whether the item or group can be edited
    editable = d_(Bool())
    
    #: Triggered when the item's contents change
    changed = d_(Event(), writable=False)
    
    #: Triggered when the checkbox state changes
    toggled = d_(Event(bool), writable=False)
    
    @observe('row', 'column', 'text', 'text_alignment', 'icon', 'icon_size',
             'selectable', 'selected', 'checkable', 'checked', 'editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        if change['name'] in ['row', 'column']:
            super(AbstractWidgetItem, self)._update_proxy(change)
        else:
            self.proxy.data_changed(change)

