'''
Created on Jun 3, 2015

@author: jrm
'''
from atom.api import (
    ContainerList, Typed, Bool, ForwardTyped, observe
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
        

class TreeViewItem(AbstractWidgetItem):
    #: Proxy reference
    proxy = Typed(ProxyTreeViewItem)
    
    #: The child items
    items = d_(ContainerList(default=[]))

    @observe('row')
    def _update_index(self,change):
        for column,item in enumerate(self._items):
            item.row = self.row # Row is the Parent item
            item.column = column
        
class TreeViewColumn(AbstractWidgetItem):
    """ Use this to build a table by defining the columns. 
    """
    #: Proxy reference
    proxy = Typed(ProxyTreeViewColumn)
