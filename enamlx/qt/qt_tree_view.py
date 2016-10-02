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
        if not index.isValid():
            return len(self.declaration.items)
        parent = index.internalPointer()
        d = parent.declaration._items[index.row()]
        print 'rowcount ',len(d.items),d
        return len(d.items)
    
    def columnCount(self, index):
        d = self.declaration
        if d.horizontal_headers:
            return len(d.horizontal_headers)
        elif not index.isValid():
            return 0
        parent = index.internalPointer()
        d = parent.declaration._items[index.row()]
        return len(d._columns)
    
    def index(self, row, column, parent):
        """ The index should point to the corresponding 
            QtControl in the enaml hierarchy 
        """
        item = parent.internalPointer()
        d = item.declaration if item else self.declaration
        r = row#%self.declaration.visible_rows
        print 'createIndex',d.proxy,row,column
        return self.createIndex(row,column,d.proxy)
        #return self.createIndex(row,column,d._items[r].proxy)

    def parent(self, index):
        parent = index.internalPointer()
        d = parent.declaration
        if d==self.declaration:
            return QModelIndex()
        #d = d.parent
        return self.createIndex(d.row,0,d.parent.proxy)
#         print 'parent',index.row(),index.column(),item
#         if not item or item.declaration==self.declaration:
#             return QModelIndex()
#         return item.index
        #return self.createIndex(parent.declaration.row,0,parent)

    def itemAt(self,index=None):
        if not index or not index.isValid():
            return
        item = index.internalPointer()
        d = item.declaration
        try:
            print d,d.row,d.column,index.row(),index.column()
            r = index.row()
            c = index.column()# - d.visible_column
            #: First column is the item
            return d._items[r]._columns[c].proxy
        except IndexError:
            return

class QtTreeView(QtAbstractItemView, ProxyTreeView):
    #: Tree widget
    widget = Typed(QTreeView)
    
    #: Root index
    index = Instance(QModelIndex,())
    
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
        
    def set_horizontal_headers(self, headers):
        self.widget.header().model().layoutChanged.emit()
        
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
            try:
                d.visible_column = max(0,min(value,self.model.columnCount(self.index)-d.visible_columns))
            except RuntimeError:
                pass
        
    def _refresh_visible_row(self, value):
        self._pending_row_refreshes -=1
        if self._pending_row_refreshes==0:
            d = self.declaration
            try:
                d.visible_row = max(0,min(value,self.model.rowCount(self.index)-d.visible_rows))
            except RuntimeError:
                pass
            


class AbstractQtTreeViewItem(AbstractQtWidgetItem):
    """ Base TreeViewItem class """
      
    #: Pending refreshes when loading widgets
    _refresh_count = Int(0)
    
    #: Time to wait before loading widget
    _loading_interval = Int(100)
    
    def create_widget(self):
        for child in self.children():
            if (not isinstance(child,AbstractQtTreeViewItem) 
                and isinstance(child, (Pattern, QtWidget))):
                self.delegate = child
    
    def set_row(self, row):
        self._update_index()
        
    def set_column(self,column):
        self._update_index()
        
    def _default_index(self):
        d = self.declaration
        parent_index = self.parent().index
        #print d,d.row,d.column,parent_index.row(),parent_index.column(),parent_index.internalPointer()
        return self.view.model.index(d.row,d.column,parent_index)
    
    def _update_index(self):
        self.index = self._default_index()
        print 'UPDATE',self.declaration.text,self,self.index.internalPointer(),self.index.row(),self.index.column(),self.index.parent()

        assert self == self.view.model.itemAt(self.index)
        
        if self.delegate and self.index.isValid():
            #print self.parent(),self,self.index.row(),self.index.column()
            self._refresh_count +=1
            timed_call(self._loading_interval,self._update_delegate)
    
    def _update_delegate(self):
        """ Update the delegate cell widget. This is deferred so it
        does not get called until the user is done scrolling. 
        """
        self._refresh_count -=1
        if self._refresh_count!=0:
            return
        
        #return # DISABLED
        
        try:
            delegate = self.delegate
            if not self._is_visible():
                return
            
            print self,self.index.row(),self.index.column(),self.index.internalPointer()
            # The table destroys when it goes out of view
            # so we always have to make a new one
            delegate.create_widget()
            delegate.init_widget()
            
            #  Set the index widget
            self.view.widget.setIndexWidget(self.index,delegate.widget)
        except RuntimeError:
            pass # Since this is deferred, the table could be deleted already
        
    def _is_visible(self):
        return self.index.isValid()
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.view.model.dataChanged.emit(self.index,self.index)
                
class QtTreeViewItem(AbstractQtTreeViewItem, ProxyTreeViewItem):
  
    def _default_view(self):
        """ If this is the root item, return the parent
            which must be a TreeView, otherwise return the
            parent Item's view.
        """
        parent = self.parent()
        if isinstance(parent, QtTreeView):
            return parent
        return parent.view
        
        
class QtTreeViewColumn(AbstractQtTreeViewItem,ProxyTreeViewColumn):
    
#     def _default_index(self):
#         d = self.declaration
#         # Return index that will retreive this column
#         index = self.view.model.index(d.row,d.column,self.parent().index)#.parent().index)
#         #index = super(QtTreeViewColumn, self)._default_index()
#         print "column index ({},{}) is {}".format(d.row,d.column,index)
#         return index
    
    def _default_view(self):
        """ Since the TreeViewColumn must be a child of a TreeViewItem,
            simply return the Item's view.
        """
        return self.parent().view
        
