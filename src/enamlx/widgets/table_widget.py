'''
Created on Jun 3, 2015

@see: https://github.com/nucleic/enaml/issues/71 

@author: jrm
'''
from atom.atom import set_default
from atom.api import (ContainerList, Int, Coerced,  Unicode, Event, Typed, Bool, ForwardTyped, observe)
from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl
from enaml.icon import Icon
from enaml.layout.geometry import Size
from enamlx.widgets.abstract_item_view import AbstractItemView

class ProxyTableWidget(ProxyControl):
    declaration = ForwardTyped(lambda: TableWidget)
    
    def set_current_row(self,row):
        raise NotImplementedError
    
    def set_current_column(self,column):
        raise NotImplementedError
    
class ProxyTableWidgetRow(ProxyControl):
    declaration = ForwardTyped(lambda: TableWidgetRow)
    
    def set_row(self,row):
        raise NotImplementedError
    
class ProxyTableWidgetColumn(ProxyControl):
    declaration = ForwardTyped(lambda: TableWidgetColumn)
    
    def set_column(self,column):
        raise NotImplementedError
    
class ProxyTableWidgetItem(ProxyControl):
    declaration = ForwardTyped(lambda: TableWidgetItem)
    
    def set_checked(self, checked):
        raise NotImplementedError
    
    def set_icon(self, icon):
        raise NotImplementedError
    
    def set_selected(self, selected):
        raise NotImplementedError
    
    def set_data(self, (role,value)):
        raise NotImplementedError
    
    def set_text(self, text):
        raise NotImplementedError
    
    def set_text_alignment(self, alignment):
        raise NotImplementedError
    
    def set_flags(self, flags):
        raise NotImplementedError
    
class TableWidget(AbstractItemView):
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')
    proxy = Typed(ProxyTableWidget)
    
    auto_resize_columns = d_(Bool(True))
    
    show_grid = d_(Bool(True))
    word_wrap = d_(Bool(False))
    
    show_vertical_header = d_(Bool(True))
    vertical_stretch = d_(Bool(False))
    
    show_horizontal_header = d_(Bool(True))
    horizontal_stretch = d_(Bool(False))
    
    sortable = d_(Bool(True))
    headers = d_(ContainerList(Unicode()))
    
    current_row = d_(Int())
    current_column = d_(Int())
    
    def items(self):
        """ Get the items defined in the TableWidget.
        A table item is one of TableWidgetItem.
        """
        allowed = (TableWidgetRow,TableWidgetColumn,TableWidgetItem)
        return [c for c in self.children if isinstance(c, allowed)]
    
    @observe('sortable','headers','word_wrap','auto_resize_columns','current_index',
             'show_grid','show_vertical_header','show_horizontal_header',
             'vertical_stretch','horizontal_stretch',
             )
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(TableWidget, self)._update_proxy(change)
        
class AbstractTableWidgetItem(Control):
    row = d_(Int())
    column = d_(Int())
    checked = d_(Bool())
    selected = d_(Bool())
    
    checkable = d_(Bool())
    selectable = d_(Bool())
    editable = d_(Bool())
    
    toggled = d_(Event(bool), writable=False) # Called when checkbox state changes
    clicked = d_(Event(), writable=False) # Called when clicked
    double_clicked = d_(Event(), writable=False) # Called when double clicked
    
    changed = d_(Event(), writable=False) # Called when data changes
    
    entered = d_(Event(), writable=False) # Called when data changes
    pressed = d_(Event(), writable=False) # Called when data changes
    selection_changed = d_(Event(bool), writable=False) # Called when data changes
    
    @observe('row','column','checked','selected','checkable','selectable','editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(AbstractTableWidgetItem, self)._update_proxy(change)
        
class TableWidgetItem(AbstractTableWidgetItem):
    proxy = Typed(ProxyTableWidgetItem)
    text = d_(Unicode())
    icon = d_(Typed(Icon))
    
    #: The size to use for the icon. The default is an invalid size
    #: and indicates that an appropriate default should be used.
    icon_size = d_(Coerced(Size, (-1, -1)))
    tool_tip = d_(Unicode())
    data = d_(ContainerList())
    
    
    @observe('text','icon','icon_size','data','tool_tip')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(TableWidgetItem, self)._update_proxy(change)

class TableWidgetRow(AbstractTableWidgetItem):
    """ Simply a helper that sets the row for its children """

class TableWidgetColumn(AbstractTableWidgetItem):
    """ Simply a helper that sets the column for its children """


