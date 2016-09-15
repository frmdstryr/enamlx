'''
Created on Jun 3, 2015

@author: jrm
'''
from atom.api import (
    Int, Typed, ForwardTyped, observe
)
from enaml.core.declarative import d_
from enamlx.widgets.abstract_item_view import (
    AbstractItemView, ProxyAbstractItemView
)

from enamlx.widgets.abstract_item import (
    AbstractWidgetItem, AbstractWidgetItemGroup, 
    ProxyAbstractWidgetItemGroup, ProxyAbstractWidgetItem
)

class ProxyTableView(ProxyAbstractItemView):
    declaration = ForwardTyped(lambda: TableView)
    
    def get_row_count(self):
        raise NotImplementedError
    
    def get_column_count(self):
        raise NotImplemented
    
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
    
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        if change['name']=='items':
            self._update_visible_area()
        
        super(TableView, self)._update_proxy(change)
        
    def _update_visible_area(self):
        self.visible_rows = min(100,len(self.items))
        self.visible_columns = min(100,len(self.items))
        

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

