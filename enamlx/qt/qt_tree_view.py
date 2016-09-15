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
from atom.property import cached_property
from enaml.qt.qt_menu import QtMenu


class QAtomTreeModel(QAbstractAtomItemModel, QAbstractItemModel):
    
    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        elif parent.isValid():
            items = parent.internalPointer().items()
        else:
            items = self.items()
        return len(items)
    
    def columnCount(self, parent):
        if parent and parent.isValid():
            return len(parent.internalPointer().columns())
        else:
            return len(self.headers)
    
    
    def index(self, row, column, parent=None):
        if parent.isValid():
            item = self.itemAt(parent)
            if item
        else:
            d = self.declaration
            return self.createIndex(row,column,QModelIndex())
            
        parent = parent or QModelIndex()
        d = self.declaration
        if not parent.isValid():
            childItem = self.items()[row]
            return self.createIndex(row, column, childItem)
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        #print("Parent of (%s,%s)"%(index.row(),index.column()))
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem==self.view:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)
    
    def itemAt(self,index):
        if not index.isValid():
            return None
        d = self.declaration
        try:
            d.current_row = index.row()
            d.current_column = index.column()
            # item = index.internalPointer().columns()[index.column()]
            #r = d.current_row - d.visible_row #% len(d._items) 
            #c = d.current_column - d.visible_column 
            return d._items[r]._items[c].proxy
        except IndexError:
            return None

class QtTreeView(QtAbstractItemView, ProxyTreeView):
    #: Tree widget
    widget = Typed(QTreeView)
    
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
        #for child in self.children():
        #    if isinstance(child,(Pattern,QtWidget)) and not isinstance(child, QtTreeViewItem):
        #        self.delegate = child
        
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
        parent = self.parent()
        parent_index = parent.index if parent!=self.view else QModelIndex()
        self.index = self.view.model.index(d.row,d.column,parent_index)
    
    def refresh_model(self, change):
        """ Notify the model that data has changed in this cell! """
        self.view.model.dataChanged.emit(self.index,self.index)
        
class QtTreeViewColumn(AbstractQtWidgetItem,ProxyTreeViewColumn):
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child
                
    def _default_view(self):
        """ Since the TreeViewColumn must be a child of a TreeViewItem,
            simply return the Item's view.
        """
        return self.parent().view
    
    def _update_index(self):
        """ The parent """
        d = self.declaration
        self.index = self.view.model.index(d.row,d.column,d.parent.index)
        
