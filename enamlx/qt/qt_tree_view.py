# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from enaml.application import timed_call
from enaml.qt.q_resource_helpers import get_cached_qicon, get_cached_qcolor
from atom.api import Typed,Instance,Int,ContainerList,observe
from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.tree_view import ProxyTreeViewItem,ProxyTreeView,ProxyTreeViewColumn
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,AbstractQtWidgetItemGroup,\
    TEXT_H_ALIGNMENTS, TEXT_V_ALIGNMENTS,RESIZE_MODES
from enaml.qt.QtGui import QTreeView
from enaml.qt.QtCore import Qt,QAbstractItemModel,QModelIndex
from enaml.core.pattern import Pattern
from enaml.qt.qt_widget import QtWidget
from atom.property import cached_property
from enaml.qt.qt_menu import QtMenu


class QAtomTreeModel(QAbstractItemModel):
    
    def __init__(self,view,*args,**kwargs):
        self.view = view # Link back to the view as we cannot inherit from Atom and QAbstractTreeModel
        self.rootItem = QtTreeViewItem(model_index=QModelIndex())
        super(QAtomTreeModel, self).__init__(*args,**kwargs)
        
    @property
    def items(self):
        return self.view.items
    
    @property
    def headers(self):
        return self.view.headers
    
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
    
    def data(self, index, role):
        item = self.itemAt(index)
        if not item:
            return None
        #if item.delegate:
            #self.view.widget.setIndexWidget(index,item.delegate.widget)
        #    return None
        #print("data(index = (%s,%s),item=%s)"%(index.row(),index.column(),item.declaration.text))
        d = item.declaration
        
        if role == Qt.DisplayRole:
            return d.text
        elif role == Qt.ToolTipRole:
            return d.tool_tip
        elif role == Qt.CheckStateRole and d.checkable:
            return d.checked and Qt.Checked or Qt.Unchecked
        elif role == Qt.DecorationRole and d.icon:
            return get_cached_qicon(d.icon)
        elif role == Qt.EditRole and d.editable:
            return d.text
        elif role == Qt.StatusTipRole:
            return d.status_tip
        elif role == Qt.TextAlignmentRole:
            h,v = d.text_alignment
            return TEXT_H_ALIGNMENTS[h] | TEXT_V_ALIGNMENTS[v]
        elif role == Qt.ForegroundRole and d.foreground:
            return get_cached_qcolor(d.foreground)
        elif role == Qt.BackgroundRole and d.background:
            return get_cached_qcolor(d.background)
        #elif role == Qt.SizeHintRole and d.width:
        #    return 
        return None
    
    def flags(self, index):
        item = self.itemAt(index)
        if not item:
            return Qt.NoItemFlags
        d = item.declaration
        flags = Qt.ItemIsEnabled
        if d.editable:
            flags |= Qt.ItemIsEditable
        if d.checkable:
            flags |= Qt.ItemIsUserCheckable
        if d.selectable:
            flags |= Qt.ItemIsSelectable
        return flags
    
    def setData(self, index,value,role=Qt.EditRole):
        item = self.itemAt(index)
        if not item:
            return False
        if role==Qt.CheckStateRole:
            checked = value==Qt.Checked
            if checked!=item.declaration.checked:
                item.declaration.checked = checked
                item.declaration.toggled(checked)
        else:
            return super(QAtomTreeModel, self).setData()
        return True
    
    def index(self, row, column, parent=None):
        parent = parent or QModelIndex()
        #print("Index=(%s,%s),Parent=(%s,%s)"%(row,column,parent.row(),parent.column()))
        #if not self.hasIndex(row, column, parent):
        #    assert False
        #    return QModelIndex()
        
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
        #self.view.visible_index = index
        #self.view.current_index = self.view.widget.currentIndex()
        item = index.internalPointer().columns()[index.column()]
        return item
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[col] # For now...
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None
    
    def clear(self):
        self.beginResetModel()
        self.view.items = []
        self.endResetModel()

class QtTreeView(QtAbstractItemView, ProxyTreeView):
    widget = Typed(QTreeView)
    
    # Contains the headers
    headers = ContainerList(default=[])
    
    model_index = Instance(QModelIndex,(),{})
    current_index = Instance(QModelIndex)
    visible_index = Instance(QModelIndex) # Last updated index
    
    # Refreshing the view on every update makes it really slow
    # So if we defer refreshing until everything is added it's fast :) 
    _pending_refreshes = Int(0)
    
    def create_widget(self):
        self.widget = QTreeView(self.parent_widget())
        self.model = QAtomTreeModel(view=self,parent=self.widget)
        
    def init_widget(self):
        super(QtTreeView, self).init_widget()
        d = self.declaration
        self.set_model(self.model)
        self.set_word_wrap(d.word_wrap)
        self.set_show_horizontal_header(d.show_horizontal_header)
        self.set_horizontal_stretch(d.horizontal_stretch)
        self.set_resize_mode(d.resize_mode)
        self.set_current_row(d.current_row)
        self.set_current_column(d.current_column)
        if d.horizontal_minimum_section_size:
            self.set_horizontal_minimum_section_size(d.horizontal_minimum_section_size)
        self.set_headers(d.headers)
        self.set_show_root(d.show_root)

         
    def init_layout(self):
        for i,item in enumerate(self.items()):
            item.model_index = self.model.index(i,0)
     
    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
           
    @observe('items','headers','declaration.iterable_index')
    def _refresh_view(self,change):
        """ Defer until later so the view is only updated after all items
        are added. """
        self._pending_refreshes +=1
        timed_call(200,self._refresh_layout)
    
    def _refresh_layout(self):
        """ Refreshes the layout only when this is the last refresh queued. """
        if self._pending_refreshes==1:
            self.model.layoutChanged.emit()
            self._refresh_sizes()
            
        self._pending_refreshes -=1
        
    def _refresh_sizes(self):
        """ Refresh column sizes when the data changes. """
        if self.items:
            header = self.widget.header()
            
            for i,item in enumerate(self.items[0]):
                header.setResizeMode(i,RESIZE_MODES[item.declaration.resize_mode])
                if item.declaration.width:
                    header.resizeSection(i,item.declaration.width)
    
                    
    def _observe_current_index(self,change):
        index = change['value']
        self.declaration.current_row = index.row()
        self.declaration.current_column = index.column()
        
    def _observe_visible_index(self,change):
        """ Determine which rows and columns are visible,
        this is hacked to work and probably wont in all cases.
        """
        index = change['value']
        # Try the simple way
        r = self.widget.rect()
        tl_index = self.widget.indexAt(r.topLeft())
        br_index = self.widget.indexAt(r.bottomRight())
        
        if not br_index.isValid():
            br_index = self.widget.indexAt(r.bottomLeft())
            if not br_index.isValid():
                br_index = index
        
        self.declaration.visible_rect = [tl_index.row(),br_index.column(),br_index.row(),tl_index.column()]
        
    #--------------------------------------------------------------------------
    # Widget Setters
    #--------------------------------------------------------------------------
    def set_iterable_index(self,index):
        pass
        
    def set_current_row(self,row):
        d = self.declaration
        index = self.model.index(max(0,d.current_row),max(0,d.current_column))
        if not index.isValid():
            return
        self.widget.scrollTo(index)
    
    def set_current_column(self,column):
        d = self.declaration
        index = self.model.index(max(0,d.current_row),max(0,d.current_column))
        if not index.isValid():
            return
        self.widget.scrollTo(index)
    
    def set_sortable(self,sortable):
        self.widget.setSortingEnabled(sortable)
        
    def set_headers(self,headers):
        self.headers = headers
        
    def set_show_grid(self,show):
        self.widget.setShowGrid(show)
        
    def set_show_root(self,show):
        self.widget.setRootIsDecorated(show)
        
    def set_word_wrap(self,wrap):
        self.widget.setWordWrap(wrap)
        
    def set_horizontal_minimum_section_size(self,size):
        self.widget.header().setMinimumSectionSize(size)
        
    def set_horizontal_stretch(self,stretch):
        self.widget.header().setStretchLastSection(stretch)
        
    def set_padding(self,padding):
        self.widget.setStyleSheet("QTreeView::item { padding: %ipx }"%padding);
    
    def set_resize_mode(self,mode):
        self.widget.header().setResizeMode(RESIZE_MODES[mode])
        
    def set_show_horizontal_header(self,show):
        header = self.widget.header()
        header.show() if show else header.hide()
        
    def set_show_vertical_header(self,show):
        header = self.widget.verticalHeader()
        header.show() if show else header.hide()
            
    def set_auto_resize_columns(self,enabled):
        return
        if enabled:
            self.widget.resizeColumnsToContents()
            
    @cached_property
    def _items(self):
        return [child for child in self.children() if isinstance(child, QtTreeViewItem) and not isinstance(child, QtTreeViewColumn)]
    
    def items(self):
        return self._items
    
    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtTreeView."""
        self.members()['_items'].reset(self)
        #if isinstance(child,(QtTreeViewItem)):
        #    self.items.append(child)
             
             
    def child_removed(self, child):
        """  Handle the child removed event for a QtTreeView."""
        self.members()['_items'].reset(self)
        #if isinstance(child,(QtTreeViewColumn)):
        #    self.items.remove(child)
        
    def destroy(self):
        self.model.clear()
        super(QtTreeView, self).destroy()
        
class AbstractQtTreeViewItemGroup(AbstractQtWidgetItemGroup):
    
    def create_widget(self):
        pass
    
    @property
    def widget(self):
        return self.parent_widget()
    
    def set_selectable(self,selectable):
        for child in self.items():
            child.declaration.selectable = selectable
            
    def set_row(self,row):
        self.declaration.row = row
        for column,child in enumerate(self.items()):
            child.declaration.row = row
            child.declaration.column = column
            
    def set_column(self,column):
        self.declaration.column = column
        for row,child in enumerate(self.items()):
            child.declaration.column = column
            child.declaration.row = row
                
                
class QtTreeViewItem(AbstractQtWidgetItem, ProxyTreeViewItem):
    widget = Instance(QTreeView)
    items = ContainerList()
    model_index = Instance(QModelIndex)
    
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child,(Pattern,QtWidget)) and not isinstance(child, QtTreeViewItem):
                self.delegate = child
            elif isinstance(child, QtMenu):
                self.menu = child
        
        if self.delegate:
            self.widget = self.parent_widget()

    def init_widget(self):
        self.set_model_index()
    
    def set_model_index(self,index=None):
        index = index or self.parent().model_index
        r,c = self.row(),self.column()
        self.model_index = self.tree_view().model.index(r,c,index)
        #print(self,self.parent(),r,c,self.model_index.row(),self.model_index.column(),index.row(),index.column(),self.delegate)
        
    
    
    def init_layout(self):
        view = self.tree_view()
        if self.delegate:
            view.widget.setIndexWidget(self.model_index,self.delegate.widget) 
            
          
         
    def refresh_model(self, change):
        """ Notify the model that data has changed in this cell! """
        parent = self.tree_view()
        return
        parent.model.dataChanged.emit(self.model_index,self.model_index)
        
    def row(self):
        parent = self.parent()
        items = parent.items()
        return items.index(self)
    
    def column(self):
        return 0 
        
    def tree_view(self):
        parent = self.parent()
        while not isinstance(parent,QtTreeView):
            parent = parent.parent()
        return parent
    
    @cached_property
    def _items(self):
        return [c for c in self.children() if isinstance(c, QtTreeViewItem) and not isinstance(c, QtTreeViewColumn)]
    
    def items(self):
        return self._items
    
    @cached_property
    def _columns(self):
        return [self] + [c for c in self.children() if isinstance(c, QtTreeViewColumn)]
    
    def columns(self):
        return self._columns
    
    def child_added(self, child):
        self.members()['_items'].reset(self)
        self.members()['_columns'].reset(self)
        
    def child_removed(self, child):
        self.members()['_items'].reset(self)
        self.members()['_columns'].reset(self)
        
    
class QtTreeViewColumn(QtTreeViewItem,ProxyTreeViewColumn):
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child
        if self.delegate:
            self.widget = self.tree_view().widget
        else:
            self.widget = self.parent_widget()
    
    def set_model_index(self,index=None):
        # Set it as index of row
        super(QtTreeViewColumn, self).set_model_index(index or self.parent().parent().model_index) 
    
    def row(self):
        return self.parent().row()
        
    def column(self):
        parent = self.parent()
        columns = parent.columns()
        return columns.index(self)
            
    #def init_layout(self):
    #    return QtTreeViewItem.init_layout(self)
    
    
    
    def _default_column(self):
        return self.parent().columns().index(self)
        
