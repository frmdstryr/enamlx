'''
Created on Jun 3, 2015

@author: jrm
'''
from atom.api import (
    ContainerList, Typed, Int, Bool, ForwardTyped, observe
)
from enaml.core.declarative import d_
from enamlx.widgets.abstract_item_view import (
    AbstractItemView,ProxyAbstractItemView
)
from enamlx.widgets.abstract_item import (
    ProxyAbstractWidgetItemGroup,ProxyAbstractWidgetItem,
    AbstractWidgetItem
)

class ProxyTreeView(ProxyAbstractItemView):
    declaration = ForwardTyped(lambda: TreeView)
    
class ProxyTreeViewColumn(ProxyAbstractWidgetItemGroup):
    declaration = ForwardTyped(lambda: TreeViewColumn)
    
    def set_column(self,column):
        raise NotImplementedError
    
class ProxyTreeViewItem(ProxyAbstractWidgetItem):
    declaration = ForwardTyped(lambda: TreeViewItem)
    
    def refresh_model(self,change):
        raise NotImplementedError
    
class TreeView(AbstractItemView):
    #: Proxy widget
    proxy = Typed(ProxyTreeView)
    
    #: Show root node
    show_root = d_(Bool(True))
    
    @observe('show_root')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        # The superclass handler implementation is sufficient.
        super(TreeView, self)._update_proxy(change)
        
    def child_added(self, child):
        super(TreeView, self).child_added(child)
        self._update_rows()
        
    def child_removed(self, child):
        super(TreeView, self).child_removed(child)
        self._update_rows()
        
    def _update_rows(self):
        for r,item in enumerate(self._items):
            item.row = r

class TreeViewItem(AbstractWidgetItem):
    #: Proxy reference
    proxy = Typed(ProxyTreeViewItem)
    
    #: The child items
    items = d_(ContainerList(default=[]))
    
    #: First visible row
    visible_row = d_(Int(0))
    
    #: Number of rows visible
    visible_rows = d_(Int(100), writable=False)
    
    #: First visible column
    visible_column = d_(Int(0))
    
    #: Number of columns visible
    visible_columns = d_(Int(1), writable=False)
    
    def _get_items(self):
        return [c for c in self.children if isinstance(c,TreeViewItem)]
    
    def child_added(self, child):
        super(TreeViewItem, self).child_added(child)
        self._update_rows()
        
    def child_removed(self, child):
        super(TreeViewItem, self).child_removed(child)
        self._update_rows()
    
    def _update_rows(self):
        """ Update the row numbers """
        for row,item in enumerate(self._items):
            item.row = row # Row is the Parent item
            item.column = 0
        
class TreeViewColumn(AbstractWidgetItem):
    """ Use this to build a table by defining the columns. 
    """
    #: Proxy reference
    proxy = Typed(ProxyTreeViewColumn)
