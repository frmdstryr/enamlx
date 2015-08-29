# -*- coding: utf-8 -*-
'''
Created on Aug 24, 2015

@author: jrm
'''
from atom.api import (Int, Enum, Bool, Unicode, ContainerList, Typed, Coerced, Event, observe)
from enaml.core.declarative import d_
from enaml.widgets.control import Control
from enaml.icon import Icon
from enaml.layout.geometry import Size

class AbstractWidgetItemGroup(Control):
    row = d_(Int())
    
    selected = d_(Bool())
    
    checked = d_(Bool())
    
    selectable = d_(Bool())
    
    editable = d_(Bool())
    
    checkable = d_(Bool())
    
    clicked = d_(Event(), writable=False) # Called when clicked
    
    double_clicked = d_(Event(), writable=False)
    
    entered = d_(Event(), writable=False)
    
    pressed = d_(Event(), writable=False)
    
    changed = d_(Event(), writable=False)
        
    selection_changed = d_(Event(bool), writable=False)
    
    # Called when checkbox state changes
    toggled = d_(Event(bool), writable=False)
    
    @observe('row','checked','selected','checkable','selectable','editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractWidgetItemGroup, self)._update_proxy(change)


class AbstractWidgetItem(AbstractWidgetItemGroup):
    
    text = d_(Unicode())
    
    text_alignment = d_(Enum(*[(h,v) for h in ('left','right','center','justify') for v in ('center','top','bottom')]))
    
    width = d_(Int())
    
    tool_tip = d_(Unicode())
    
    icon = d_(Typed(Icon))
    
    #: The size to use for the icon. The default is an invalid size
    #: and indicates that an appropriate default should be used.
    icon_size = d_(Coerced(Size, (-1, -1)))
    
    data = d_(ContainerList())
    
    @observe('text','icon','icon_size','data','tool_tip','width','text_alignment')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractWidgetItem, self)._update_proxy(change)

