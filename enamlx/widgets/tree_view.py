"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Jun 3, 2015
"""
from atom.api import (
    ContainerList, Typed, Int, Bool, Property, ForwardTyped, observe
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
    
    def set_column(self, column):
        raise NotImplementedError


class ProxyTreeViewItem(ProxyAbstractWidgetItem):
    declaration = ForwardTyped(lambda: TreeViewItem)
    
    def refresh_model(self, schange):
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
        for r, item in enumerate(self._items):
            item.row = r


class TreeViewItem(AbstractWidgetItem):
    #: Proxy reference
    proxy = Typed(ProxyTreeViewItem)
    
    #: The child items
    items = d_(ContainerList(default=[]))
    
    #: First visible row
    visible_row = d_(Int(0))
    
    #: Number of rows visible
    visible_rows = d_(Int(100))
    
    #: First visible column
    visible_column = d_(Int(0))
    
    #: Number of columns visible
    visible_columns = d_(Int(1))
    
    def _get_items(self):
        """ Items should be a list of child TreeViewItems excluding
            columns.
        """
        return [c for c in self.children if isinstance(c, TreeViewItem)]
    
    def _get_columns(self):
        """ List of child TreeViewColumns including 
            this item as the first column
        """
        return [self] + [c for c in self.children
                         if isinstance(c, TreeViewColumn)]
    
    #: Columns
    _columns = Property(lambda self: self._get_columns(), cached=True)
    
    def child_added(self, child):
        super(TreeViewItem, self).child_added(child)
        self.get_member('_columns').reset(self)
        self._update_rows()
        
    def child_removed(self, child):
        super(TreeViewItem, self).child_removed(child)
        self.get_member('_columns').reset(self)
        self._update_rows()

    def _update_rows(self):
        """ Update the row and column numbers of child items. """
        for row, item in enumerate(self._items):
            item.row = row  # Row is the Parent item
            item.column = 0
        
        for column, item in enumerate(self._columns):
            item.row = self.row  # Row is the Parent item
            item.column = column


class TreeViewColumn(AbstractWidgetItem):
    """ Use this to build a table by defining the columns. 
    """
    #: Proxy reference
    proxy = Typed(ProxyTreeViewColumn)
