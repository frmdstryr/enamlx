'''
Created on Jun 3, 2015

@author: jrm
'''
from atom.api import (
    ContainerList, Int, Typed, Bool,
    Enum, ForwardTyped, observe, set_default
)
from enaml.core.declarative import d_
from enaml.widgets.control import ProxyControl
from enamlx.widgets.abstract_item_view import AbstractItemView
from enamlx.widgets.abstract_item import (
    AbstractWidgetItem, AbstractWidgetItemGroup, 
    ProxyAbstractWidgetItemGroup, ProxyAbstractWidgetItem
)

class ProxyTableView(ProxyControl):
    declaration = ForwardTyped(lambda: TableView)
    
    def set_cell_padding(self,row):
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
    
    def set_items(self,items):
        pass
    
class ProxyTableViewRow(ProxyAbstractWidgetItemGroup):
    declaration = ForwardTyped(lambda: TableViewRow)
    
    def set_row(self,row):
        raise NotImplementedError
    
class ProxyTableViewColumn(ProxyAbstractWidgetItemGroup):
    declaration = ForwardTyped(lambda: TableViewColumn)
    
    def set_column(self,column):
        raise NotImplementedError
    
class ProxyTableViewItem(ProxyAbstractWidgetItem):
    declaration = ForwardTyped(lambda: TableViewItem)
    
    def data_changed(self,change):
        raise NotImplementedError
    
class TableView(AbstractItemView):
    #: Proxy reference
    proxy = Typed(ProxyTableView)
    
    #: Table should expand by default
    hug_width = set_default('ignore')
    
    #: Table should expand by default
    hug_height = set_default('ignore')
    
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
    
    @observe('cell_padding','auto_resize','resize_mode','show_grid','word_wrap',
             'show_horizontal_header','horizontal_headers','horizontal_stretch',
             'show_vertical_header','vertical_header','vertical_stretch')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        if change['name']=='items':
            self.visible_rows = min(100,len(self.items))
        # The superclass handler implementation is sufficient.
        super(TableView, self)._update_proxy(change)
        

class TableViewItem(AbstractWidgetItem):
    """ The base class implementation is sufficient. """
        
class TableViewRow(AbstractWidgetItemGroup):
    """ Use this to build a table by defining the rows. 
    """
    #: Row within the table
    row = d_(Int())
    
    @observe('row')
    def _update_index(self,change):
        for column,item in enumerate(self._items):
            item.row = self.row
            item.column = column

class TableViewColumn(AbstractWidgetItemGroup):
    """ Use this to build a table by defining the columns. 
    """
    #: Column within the table
    column = d_(Int())

    @observe('column')
    def _update_index(self,change):
        for row,item in enumerate(self._item):
            item.row = row
            item.column = self.column

