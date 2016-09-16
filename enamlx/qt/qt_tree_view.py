# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from atom.api import (
    Typed, Instance, Int, ContainerList, observe
)
from enaml.application import timed_call

from enamlx.qt.qt_abstract_item_view import QtAbstractItemView,\
    QAbstractAtomItemModel
from enamlx.widgets.tree_view import ProxyTreeViewItem,ProxyTreeView,ProxyTreeViewColumn
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,AbstractQtWidgetItemGroup,RESIZE_MODES
from enaml.qt.QtGui import QTreeView
from enaml.qt.QtCore import Qt,QAbstractItemModel,QModelIndex
from enaml.core.pattern import Pattern
from enaml.qt.qt_widget import QtWidget
from enaml.qt.qt_control import QtControl
import traceback

class QAtomTreeModel(QAbstractAtomItemModel, QAbstractItemModel):
    
    def rowCount(self, index):
        print "rowCount({})".format(index)
        d = self.declaration
        if d.vertical_headers:
            return len(d.vertical_headers)
        item = self.itemAt(index)
        d = item.declaration if item else self.declaration
        print len(d.items)
        return len(d.items)
    
    def columnCount(self, index):
        print "columnCount({})".format(index)
        d = self.declaration
        if d.horizontal_headers:
            print "horizontal headers"
            return len(d.horizontal_headers)
        item = self.itemAt(index)
        if not item:
            return 0
        d = item.declaration
        return len(d.items)
    
    def data(self, index, role):
        print "data({},{})".format(index,role)
        return super(QAtomTreeModel, self).data(index,role)
    
#     def hasChildren(self, index):
#         item = self.itemAt(index)
#         if not item:
#             return False
#         d = item.declaration
#         return bool(d.items)
        
    def index(self, row, column, parent):
        """ The index should point to the corresponding QtControl in the 
            enaml hierarchy 
        """
        print "index({},{},{})".format(row,column,parent)
        if parent and parent.isValid():
            item = self.itemAt(parent)
            return self.createIndex(row,column,item.declaration._items[row].proxy)
        else:
            return self.createIndex(row,column,self.declaration._items[row].proxy) 

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        parent = item.parent()
        d = parent.declaration
        if d==self.declaration:
            return QModelIndex()
        return self.createIndex(d.row, 0, parent)
     
    def itemAt(self,index):
        #print 'itemAt({})'.format(index)
        if not index.isValid():
            return
        item = index.internalPointer()
        print "itemAt {} is {}".format(index,item)
        d = item.declaration
        try:
            #d.current_row = index.row()
            #d.current_column = index.column()
            # item = index.internalPointer().columns()[index.column()]
            
            r,c = index.row(),index.column()#d.current_row,d.current_column
            print r,c
            #if r!=0:
            #    d = d.children[r-1]
                
            if c == 0:
                return d.proxy
            return d._items[c-1].proxy
                
            
        except IndexError:
            return None

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
        
    def set_resize_mode(self,mode):
        self.widget.header().setResizeMode(RESIZE_MODES[mode])
        
    def set_show_horizontal_header(self,show):
        header = self.widget.header()
        header.show() if show else header.hide()
        
                
class QtTreeViewItem(AbstractQtWidgetItem, ProxyTreeViewItem):
    
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
        
    def _update_index(self):
        d = self.declaration
        #parent = self.parent()
        #parent_index = parent.index if parent!=self.view else QModelIndex()
        self.index = self.view.model.index(d.row,d.column,self.parent().index)#.parent())
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.view.model.dataChanged.emit(self.index,self.index)
        
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
        d = self.declaration
        self.index = self.view.model.index(d.row,d.column,self.parent().index)
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.view.model.dataChanged.emit(self.index,self.index)
    
        
