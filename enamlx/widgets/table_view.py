'''
Created on Jun 3, 2015

@author: jrm
'''
from atom.api import (
    ContainerList, Int, Unicode, Typed, Bool,Instance,
    Enum, ForwardTyped, observe, set_default
)
from collections import Iterable
from enaml.core.declarative import d_
from enaml.widgets.control import ProxyControl
from enamlx.widgets.abstract_item_view import AbstractItemView
from enamlx.widgets.abstract_item import (
    AbstractWidgetItem, AbstractWidgetItemGroup
)

class ProxyTableView(ProxyControl):
    declaration = ForwardTyped(lambda: TableView)
    
    def set_current_row(self,row):
        pass
    
    def set_current_column(self,column):
        raise NotImplementedError
    
class ProxyTableViewRow(ProxyControl):
    declaration = ForwardTyped(lambda: TableViewRow)
    
    def set_row(self,row):
        raise NotImplementedError
    
class ProxyTableViewColumn(ProxyControl):
    declaration = ForwardTyped(lambda: TableViewColumn)
    
    def set_column(self,column):
        raise NotImplementedError
    
class ProxyTableViewItem(ProxyControl):
    declaration = ForwardTyped(lambda: TableViewItem)
    
    def refresh_model(self,change):
        raise NotImplementedError
    
class TableView(AbstractItemView):
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')
    proxy = Typed(ProxyTableView)
    
    padding = d_(Int(3))
    
    auto_resize_columns = d_(Bool(True))
    resize_mode = d_(Enum('interactive','fixed','stretch','resize_to_contents','custom'))
    
    show_grid = d_(Bool(True))
    word_wrap = d_(Bool(False))
    
    show_vertical_header = d_(Bool(True))
    vertical_stretch = d_(Bool(False))
    vertical_minimum_section_size = d_(Int(0))
    
    show_horizontal_header = d_(Bool(True))
    horizontal_stretch = d_(Bool(False))
    horizontal_minimum_section_size = d_(Int(0))
    
    sortable = d_(Bool(True))
    headers = d_(ContainerList(Unicode()))
    
    current_row = d_(Int(),writable=False)
    current_column = d_(Int(),writable=False)
    
    
    
    visible_rows = d_(Int(),writable=False)
    visible_columns = d_(Int(),writable=False)
    
    #: The iterable to use when creating the items for the looper.
    iterable = d_(Instance(Iterable))
    
    # Where our data comes from
    iterable_index = d_(Int(0)) # Current fetch index
    iterable_fetch_size = d_(Int(200)) # fetch results
    iterable_prefetch = d_(Int(20)) # Fetch when we get this far away
    
    def items(self):
        """ Get the items defined in the TableView.
        A table item is one of TableViewItem.
        """
        allowed = (TableViewRow,TableViewColumn,TableViewItem)
        return [c for c in self.children if isinstance(c, allowed)]
    
    @observe('sortable','headers','word_wrap','auto_resize_columns','current_index',
             'show_grid','show_vertical_header','show_horizontal_header','resize_mode',
             'vertical_stretch','horizontal_stretch','padding',
             )
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(TableView, self)._update_proxy(change)
        

class TableViewItem(AbstractWidgetItem):
    proxy = Typed(ProxyTableViewItem)
    resize_mode = d_(Enum('interactive','fixed','stretch','resize_to_contents','custom'))
    column = d_(Int())
    
    @observe('text','icon','icon_size','data','tool_tip','width','text_alignment',
             'row','checked','selected','checkable','selectable','editable','resize_mode')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        self.proxy.refresh_model(change)
    
class TableViewRow(AbstractWidgetItemGroup):
    """ Use this to build a table by defining the rows. 
    """
    column = d_(Int())
    
    @observe('row','checked','selected','checkable','selectable','editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        pass
        #self.proxy.refresh(change)
        
class TableViewColumn(AbstractWidgetItemGroup):
    """ Use this to build a table by defining the columns. 
    """
    column = d_(Int())

    @observe('row','checked','selected','checkable','selectable','editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        pass
        #self.proxy.refresh(change)

