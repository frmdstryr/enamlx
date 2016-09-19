# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from atom.api import (
    Typed, Instance, Property
)
from enamlx.qt.qt_abstract_item_view import (
    QtAbstractItemView, QAbstractAtomItemModel
)
from enamlx.widgets.tree_view import (
    ProxyTreeViewItem, ProxyTreeView ,ProxyTreeViewColumn
)
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem, RESIZE_MODES
from enaml.qt.QtGui import QTreeView
from enaml.qt.QtCore import Qt, QAbstractItemModel, QModelIndex
from enaml.core.pattern import Pattern
from enaml.qt.qt_widget import QtWidget

class QAtomTreeModel(QAbstractAtomItemModel, QAbstractItemModel):
    
    def rowCount(self, index=None):
        d = self.declaration
        if d.vertical_headers:
            return len(d.vertical_headers)
        item = self.itemAt(index)
        d = item.declaration if item else self.declaration
        return len(d.items)
    
    def columnCount(self, index=None):
        d = self.declaration
        if d.horizontal_headers:
            return len(d.horizontal_headers)
        item = self.itemAt(index)
        if not item:
            return 0
        d = item.declaration
        return len(d.items)
    
    def index(self, row, column, parent):
        """ The index should point to the corresponding 
            QtControl in the enaml hierarchy 
        """
        if not parent or not parent.isValid():
            d = self.declaration
            return self.createIndex(row,column,d.proxy)
        item = parent.internalPointer()
        d = item.declaration
        return self.createIndex(row,column,d._items[row].proxy)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if item.declaration == self.declaration:
            return QModelIndex()
        parent = item.parent()
        return self.createIndex(0, 0, parent)
     
    def itemAt(self,index=None):
        if not index or not index.isValid():
            return
        parent = index.internalPointer()
        d = parent.declaration
        try:
            r = index.row() - d.visible_row
            c = index.column() - d.visible_column
            #: First column is the item
            return parent._items[r]._columns[c]
        except IndexError:
            return None

class QtTreeView(QtAbstractItemView, ProxyTreeView):
    #: Tree widget
    widget = Typed(QTreeView)
    
    #: Root index
    index = Instance(QModelIndex,())
    
    def _get_items(self):
        return [c for c in self.children() if isinstance(c,QtTreeViewItem)]
    
    #: Internal items
    #: TODO: Is a cached property the right thing to use here??
    #: Why not a list??
    _items = Property(lambda self:self._get_items(),cached=True)
    
    
    def create_widget(self):
        self.widget = QTreeView(self.parent_widget())
        
    def init_widget(self):
        super(QtTreeView, self).init_widget()
        d = self.declaration
        self.set_show_root(d.show_root)
        
    def init_model(self):
        self.set_model(QAtomTreeModel(parent=self.widget))
     
    #--------------------------------------------------------------------------
    # Widget Setters
    #--------------------------------------------------------------------------
    def set_show_root(self,show):
        self.widget.setRootIsDecorated(show)
        
    def set_cell_padding(self,padding):
        self.widget.setStyleSheet("QTreeView::item { padding: %ipx }"%padding);
        
    def set_horizontal_minimum_section_size(self,size):
        self.widget.header().setMinimumSectionSize(size)
        
    def set_horizontal_stretch(self,stretch):
        self.widget.header().setStretchLastSection(stretch)
        
    def set_resize_mode(self,mode):
        self.widget.header().setResizeMode(RESIZE_MODES[mode])
        
    def set_show_horizontal_header(self,show):
        header = self.widget.header()
        header.show() if show else header.hide()
        
    def set_model(self, model):
        super(QtTreeView, self).set_model(model)
        self.index = self.model.index(0,0,None)
        
    #--------------------------------------------------------------------------
    # View refresh handlers
    #--------------------------------------------------------------------------
    def _refresh_visible_column(self, value):
        self._pending_column_refreshes -=1
        if self._pending_column_refreshes==0:
            d = self.declaration
            # TODO: What about parents???
            d.visible_column = max(0,min(value,self.model.columnCount()-d.visible_columns))
        
    def _refresh_visible_row(self, value):
        self._pending_row_refreshes -=1
        if self._pending_row_refreshes==0:
            d = self.declaration
            d.visible_row = max(0,min(value,self.model.rowCount()-d.visible_rows))
            

        
                
class QtTreeViewItem(AbstractQtWidgetItem, ProxyTreeViewItem):
    
    def _get_items(self):
        """ Get the child items of this node"""
        return [c for c in self.children() if isinstance(c,QtTreeViewItem)]
    
    def _get_columns(self):
        """ Get the columns of this node"""
        return [self]+[c for c in self.children() if isinstance(c,QtTreeViewColumn)]
    
    _columns = Property(lambda self:self._get_columns(),cached=True)
    
    def create_widget(self):
        pass
    
    def init_layout(self):
        self._update_layout()
        super(QtTreeViewItem, self).init_layout()
        
    def _update_layout(self):
        for r,child in enumerate(self._items):
            child.declaration.row = r
        
    def _default_view(self):
        """ If this is the root item, return the parent
            which must be a TreeView, otherwise return the
            parent Item's view.
        """
        parent = self.parent()
        if isinstance(parent, QtTreeView):
            return parent
        return parent.view
        
    def _update_index(self):
        d = self.declaration
        #parent = self.parent()
        #parent_index = parent.index if parent!=self.view else QModelIndex()
        self.index = self.view.model.index(d.row,d.column,self.parent().index)#.parent())
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        #return # For now
        self.view.model.dataChanged.emit(self.index,self.index)
        
    def child_added(self, child):
        super(QtTreeViewItem, self).child_added(child)
        self.get_member('_columns').reset(self)
        
    def child_removed(self, child):
        super(QtTreeViewItem, self).child_removed(child)
        self.get_member('_columns').reset(self)
        
class QtTreeViewColumn(AbstractQtWidgetItem,ProxyTreeViewColumn):
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child
                
    def set_column(self,column):
        pass
                
    def _default_view(self):
        """ Since the TreeViewColumn must be a child of a TreeViewItem,
            simply return the Item's view.
        """
        return self.parent().view
    
    def _update_index(self):
        """ The parent """
        return
        d = self.declaration
        self.index = self.view.model.index(d.row,d.column,self.parent().index)
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        return # For now
        self.view.model.dataChanged.emit(self.index,self.index)
    
        
