# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from atom.api import (
    Typed, Instance, Property, Int
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
from enaml.application import timed_call

class QAtomTreeModel(QAbstractAtomItemModel, QAbstractItemModel):
    
    def rowCount(self, index):
        #print 'rowCount',index.row(),index.column(),index.internalPointer()
        d = self.declaration
        if d.vertical_headers:
            return len(d.vertical_headers)
        elif index.column()>0:
            return 0
        item = self.itemAt(index)
        if item:
            d = item.declaration
        return len(d.items)
    
    def columnCount(self, index):
        #print 'columnCount',index.row(),index.column()
        d = self.declaration
        if d.horizontal_headers:
            return len(d.horizontal_headers)
        elif index.column()>0:
            return 0
        item = self.itemAt(index)
        if not item:
            return 0
        d = item.declaration
        return len(d.proxy._columns)
    
    def index(self, row, column, parent):
        """ The index should point to the corresponding 
            QtControl in the enaml hierarchy 
        """
        d = self.declaration
        if parent.isValid():
            item = self.itemAt(parent)
            if item:
                d = item.declaration
        return self.createIndex(row,column,d.proxy)
        #print "index ({},{}) of {} is {}".format(row,column,d,item)
        #return index
 
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        parent = index.internalPointer()
        return parent.index

    def itemAt(self,index=None):
        if not index or not index.isValid():
            return
        parent = index.internalPointer()
        d = parent.declaration
        try:
            r = index.row() - d.visible_row
            c = index.column() - d.visible_column
            #: First column is the item
            #print parent,[it.declaration.text for it in parent._items],r,c
            return parent._items[r]._columns[c]
        except IndexError as e:
            #print e
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
        
    #--------------------------------------------------------------------------
    # View refresh handlers
    #--------------------------------------------------------------------------
    def _refresh_visible_column(self, value):
        self._pending_column_refreshes -=1
        if self._pending_column_refreshes==0:
            d = self.declaration
            # TODO: What about parents???
            d.visible_column = max(0,min(value,self.model.columnCount(self.index)-d.visible_columns))
        
    def _refresh_visible_row(self, value):
        self._pending_row_refreshes -=1
        if self._pending_row_refreshes==0:
            d = self.declaration
            d.visible_row = max(0,min(value,self.model.rowCount(self.index)-d.visible_rows))
            


class AbstractQtTreeViewItem(AbstractQtWidgetItem):
    """ Base TreeViewItem class """
      
    #: Pending refreshes when loading widgets
    _refresh_count = Int(0)
    
    #: Time to wait before loading widget
    _loading_interval = Int(100)
    
    def set_row(self, row):
        self._update_index()
        
    def _default_index(self):
        d = self.declaration
        return self.view.model.index(d.row,d.column,self.parent().index)
    
    def _update_index(self):
        self.index = self._default_index()
        if self.delegate:
            self._refresh_count +=1
            timed_call(self._loading_interval,self._update_delegate)
    
    def _update_delegate(self):
        """ Update the delegate cell widget. This is deferred so it
        does not get called until the user is done scrolling. 
        """
        self._refresh_count -=1
        if self._refresh_count!=0:
            return
        
        return # DISABLED
        
        try:
            delegate = self.delegate
            if not self._is_visible():
                return
            # The table destroys when it goes out of view
            # so we always have to make a new one
            delegate.create_widget()
            delegate.init_widget()
            
            #  Set the index widget
            self.view.widget.setIndexWidget(self.index,delegate.widget)
        except RuntimeError:
            pass # Since this is deferred, the table could be deleted already
        
    def _is_visible(self):
        return True
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.view.model.dataChanged.emit(self.index,self.index)
                
class QtTreeViewItem(AbstractQtTreeViewItem, ProxyTreeViewItem):
  
    def _get_items(self):
        """ Get the child items of this node"""
        return [c for c in self.children() if isinstance(c,QtTreeViewItem)]
    
    def _get_columns(self):
        """ Get the columns of this node"""
        return [self]+[c for c in self.children() if isinstance(c,QtTreeViewColumn)]
    
    _columns = Property(lambda self:self._get_columns(),cached=True)
    
    def create_widget(self):
        pass
    
    def _default_view(self):
        """ If this is the root item, return the parent
            which must be a TreeView, otherwise return the
            parent Item's view.
        """
        parent = self.parent()
        if isinstance(parent, QtTreeView):
            return parent
        return parent.view
        
    def child_added(self, child):
        super(QtTreeViewItem, self).child_added(child)
        self.get_member('_columns').reset(self)
        
    def child_removed(self, child):
        super(QtTreeViewItem, self).child_removed(child)
        self.get_member('_columns').reset(self)
        
class QtTreeViewColumn(AbstractQtTreeViewItem,ProxyTreeViewColumn):
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child
                
    def set_column(self,column):
        self._update_index()
                
    def _default_view(self):
        """ Since the TreeViewColumn must be a child of a TreeViewItem,
            simply return the Item's view.
        """
        return self.parent().view
    
    def _default_index(self):
        d = self.declaration
        return self.view.model.index(d.row,d.column,self.parent().index)
        
