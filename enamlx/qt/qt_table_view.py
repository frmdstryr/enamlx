# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from atom.api import Typed, Instance, Int, Bool, observe
from enaml.application import timed_call
from enaml.qt.q_resource_helpers import get_cached_qicon, get_cached_qcolor
from enaml.qt.QtGui import QTableView
from enaml.qt.QtCore import Qt, QAbstractTableModel, QModelIndex

from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.table_view import ProxyTableViewItem,ProxyTableView,ProxyTableViewColumn,ProxyTableViewRow
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,AbstractQtWidgetItemGroup,\
    TEXT_H_ALIGNMENTS, TEXT_V_ALIGNMENTS,RESIZE_MODES

    

class QAtomTableModel(QAbstractTableModel):
    """ Model that pulls it's data from the TableViewItems """
    
    def setDeclaration(self,declaration):
        self.declaration = declaration
    
    def rowCount(self, parent=None):
        d = self.declaration
        if d.vertical_headers:
            return len(d.vertical_headers)
        return len(d.items)
    
    def columnCount(self, parent=None):
        d = self.declaration
        if d.horizontal_headers:
            return len(d.horizontal_headers)
        return len(d.items)
    
    def data(self, index, role):
        item = self.itemAt(index)
        if not item:
            return None
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
        #    return 20 
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
    
    def setData(self, index, value, role=Qt.EditRole):
        item = self.itemAt(index)
        if not item:
            return False
        d = item.declaration
        if role==Qt.CheckStateRole:
            checked = value==Qt.Checked
            if checked!=d.checked:
                d.checked = checked
                d.toggled(checked)
            return True
        elif role==Qt.EditRole:
            if value != d.text:
                d.text = value
            return True
        return super(QAtomTableModel, self).setData(index, value, role)
    
    def itemAt(self,index):
        if not index.isValid():
            return None
        d = self.declaration
        try:
            d.current_row = index.row()
            d.current_column = index.column()
            r = d.current_row - d.visible_row #% len(d._items) 
            c = d.current_column - d.visible_column 
            return d._items[r]._items[c].proxy
        except IndexError:
            return None
        
    def headerData(self, index, orientation, role):
        d = self.declaration
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return d.horizontal_headers[index] if d.horizontal_headers else index
            except IndexError:
                return index
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            try:
                return d.vertical_headers[index] if d.vertical_headers else index
            except IndexError:
                return index
        return None
    
    def clear(self):
        self.beginResetModel()
        try:
            self.declaration.items = []
        except:
            pass
        self.endResetModel()


class QtTableView(QtAbstractItemView, ProxyTableView):
    #: Proxy widget
    widget = Typed(QTableView)
    
    # Refreshing the view on every update makes it really slow
    # So if we defer refreshing until everything is added it's fast :) 
    _pending_refreshes = Int(0)
    
    def create_widget(self):
        self.widget = QTableView(self.parent_widget())
        
    def init_widget(self):
        super(QtTableView, self).init_widget()
        
        #: Enable context menus
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        d = self.declaration
        self.set_model(QAtomTableModel(parent=self.widget))
        self.set_show_grid(d.show_grid)
        self.set_word_wrap(d.word_wrap)
        self.set_show_vertical_header(d.show_vertical_header)
        self.set_show_horizontal_header(d.show_horizontal_header)
        self.set_horizontal_stretch(d.horizontal_stretch)
        self.set_vertical_stretch(d.vertical_stretch)
        self.set_resize_mode(d.resize_mode)
        if d.cell_padding:
            self.set_cell_padding(d.cell_padding)
        if d.vertical_minimum_section_size:
            self.set_vertical_minimum_section_size(d.vertical_minimum_section_size)
        if d.horizontal_minimum_section_size:
            self.set_horizontal_minimum_section_size(d.horizontal_minimum_section_size)
        self._refresh_visible_rows()
        self._refresh_visible_columns()
    
    def init_signals(self):
        super(QtTableView, self).init_signals()
        self.widget.horizontalScrollBar().valueChanged.connect(self._on_horizontal_scrollbar_moved)
        self.widget.verticalScrollBar().valueChanged.connect(self._on_vertical_scrollbar_moved)
     
    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
           
    @observe('items')
    def _refresh_view(self,change):
        """ Defer until later so the view is only updated after all items
        are added. """
        self._pending_refreshes +=1
        timed_call(100,self._refresh_layout)
    
    def _refresh_layout(self):
        """ Refreshes the layout only when this is the last refresh queued. """
        self._pending_refreshes -=1
        if self._pending_refreshes==0:
            try:
                self.model.layoutChanged.emit()
            except RuntimeError:
                # View can be destroyed before we get here
                return
            self._refresh_sizes()
            
    def _refresh_sizes(self):
        """ Refresh column sizes when the data changes. """
        pass
#         header = self.widget.horizontalHeader()
#         
#         for i,item in enumerate(self.items[0]):
#             header.setResizeMode(i,RESIZE_MODES[item.declaration.resize_mode])
#             if item.declaration.width:
#                 header.resizeSection(i,item.declaration.width)
    
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def _on_horizontal_scrollbar_moved(self,value):
        d = self.declaration
        d.visible_column = max(0,min(value,self.model.columnCount()-d.visible_columns))
    
    def _on_vertical_scrollbar_moved(self,value):
        d = self.declaration
        d.visible_row = max(0,min(value,self.model.rowCount()-d.visible_rows))
    
    def _refresh_visible_rows(self):
        top = self.widget.rowAt(self.widget.rect().top())
        bottom = self.widget.rowAt(self.widget.rect().bottom())
        self.declaration.visible_rows = max(1,(bottom-top))*2 # 2x for safety 
    
    def _refresh_visible_columns(self):
        left = self.widget.rowAt(self.widget.rect().left())
        right = self.widget.rowAt(self.widget.rect().right())
        self.declaration.visible_columns = max(1,(right-left))*2  
    
    #--------------------------------------------------------------------------
    # Widget Setters
    #--------------------------------------------------------------------------
    
    def set_model(self,model):
        if isinstance(model,QAtomTableModel):
            model.setDeclaration(self.declaration)
        self.widget.setModel(model)
        
    def set_sortable(self,sortable):
        self.widget.setSortingEnabled(sortable)
        
    def set_show_grid(self,show):
        self.widget.setShowGrid(show)
        
    def set_word_wrap(self,wrap):
        self.widget.setWordWrap(wrap)
        
    def set_vertical_minimum_section_size(self,size):
        self.widget.verticalHeader().setMinimumSectionSize(size)
        
    def set_horizontal_minimum_section_size(self,size):
        self.widget.horizontalHeader().setMinimumSectionSize(size)
        
    def set_horizontal_stretch(self,stretch):
        self.widget.horizontalHeader().setStretchLastSection(stretch)
        
    def set_vertical_stretch(self,stretch):
        self.widget.verticalHeader().setStretchLastSection(stretch)
    
    def set_cell_padding(self,padding):
        self.widget.setStyleSheet("QTableView::item { padding: %ipx }"%padding);
    
    def set_resize_mode(self,mode):
        self.widget.horizontalHeader().setResizeMode(RESIZE_MODES[mode])
        
    def set_show_horizontal_header(self,show):
        header = self.widget.horizontalHeader()
        header.show() if show else header.hide()
        
    def set_show_vertical_header(self,show):
        header = self.widget.verticalHeader()
        header.show() if show else header.hide()
            
    def set_auto_resize_columns(self,enabled):
        return
        if enabled:
            self.widget.resizeColumnsToContents()
            
    def set_items(self, items):
        self._refresh_view({})
            
    def destroy(self):
        """ Make sure all the table widgets are destroyed first."""
        self.model.clear()
        super(QtTableView, self).destroy()
    
class AbstractQtTableViewItemGroup(AbstractQtWidgetItemGroup):
    
    def create_widget(self):
        pass
    
    @property
    def widget(self):
        return self.parent_widget()
    
class QtTableViewItem(AbstractQtWidgetItem, ProxyTableViewItem):
    #: Index within the table
    index = Instance(QModelIndex)
    
    #: Pending refreshes when loading widgets
    _refresh_count = Int(0)
    
    #: Time to wait before loading widget
    _loading_interval = Int(100) 

    def init_widget(self):
        self._update_index()
        return # do nothing as there is no widget!
    
    @property
    def table(self):
        return self.parent().parent()
    
    def set_row(self,row):
        self._update_index()
                
    def set_column(self,column):
        self._update_index()
    
    def _update_index(self):
        """ Update the reference to the index within the table """ 
        d = self.declaration
        self.index = self.table.model.index(d.row,d.column)
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
        d = self.declaration
        
        if not self._is_visible():
            return
        # The table destroys when it goes out of view
        # so we always have to make a new one
        self.delegate.create_widget()
        self.delegate.init_widget()
        
        #  Set the index widget
        self.table.widget.setIndexWidget(self.index,self.delegate.widget)
        
    def _is_visible(self):
        """ Check if this index is currently visible """
        return True
        #d = self.table.declaration
        #return self.declaration.row
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.table.model.dataChanged.emit(self.index,self.index)
                
        
class QtTableViewRow(AbstractQtTableViewItemGroup, ProxyTableViewRow):
    
    def init_widget(self):
        d = self.declaration
        self.set_row(d.row)
        
    def set_row(self,row):
        for column,child in enumerate(self._items):
            d = child.declaration
            d.row = row
            d.column = column
            

class QtTableViewColumn(AbstractQtTableViewItemGroup, ProxyTableViewColumn):
    
    def init_widget(self):
        d = self.declaration
        self.set_column(d.column)
        
    def set_column(self, column):
        for row,child in enumerate(self._items):
            d = child.declaration
            d.row = row
            d.column = column
