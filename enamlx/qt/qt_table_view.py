# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from atom.api import Typed, Instance, Int
from enaml.application import timed_call
from enaml.qt.QtGui import QTableView
from enaml.qt.QtCore import QAbstractTableModel, QModelIndex

from enamlx.qt.qt_abstract_item_view import QtAbstractItemView, QAbstractAtomItemModel
from enamlx.widgets.table_view import (
    ProxyTableViewItem, ProxyTableView, ProxyTableViewColumn, ProxyTableViewRow
)
from enamlx.qt.qt_abstract_item import (
    AbstractQtWidgetItem, AbstractQtWidgetItemGroup,
)

    

class QAtomTableModel(QAbstractAtomItemModel,QAbstractTableModel):
    """ Model that pulls it's data from the TableViewItems """
    
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

class QtTableView(QtAbstractItemView, ProxyTableView):
    #: Proxy widget
    widget = Typed(QTableView)
    
    def create_widget(self):
        self.widget = QTableView(self.parent_widget())
    
    def init_model(self):
        self.set_model(QAtomTableModel(parent=self.widget))
    
    #--------------------------------------------------------------------------
    # View refresh handlers
    #--------------------------------------------------------------------------
    def _refresh_visible_column(self, value):
        self._pending_column_refreshes -=1
        if self._pending_column_refreshes==0:
            d = self.declaration
            d.visible_column = max(0,min(value,self.model.columnCount()-d.visible_columns))
        
    def _refresh_visible_row(self, value):
        self._pending_row_refreshes -=1
        if self._pending_row_refreshes==0:
            d = self.declaration
            d.visible_row = max(0,min(value,self.model.rowCount()-d.visible_rows))
            
    
    def _refresh_visible_rows(self):
        return
        top = self.widget.rowAt(self.widget.rect().top())
        bottom = self.widget.rowAt(self.widget.rect().bottom())
        self.declaration.visible_rows = max(1,(bottom-top))*2 # 2x for safety 
    
    def _refresh_visible_columns(self):
        return
        left = self.widget.rowAt(self.widget.rect().left())
        right = self.widget.rowAt(self.widget.rect().right())
        self.declaration.visible_columns = max(1,(right-left))*2  
    
    
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
        try:
            delegate = self.delegate
            if not self._is_visible():
                return
            # The table destroys when it goes out of view
            # so we always have to make a new one
            delegate.create_widget()
            delegate.init_widget()
            
            #  Set the index widget
            self.table.widget.setIndexWidget(self.index,delegate.widget)
        except RuntimeError:
            pass # Since this is deferred, the table could be deleted already
        
    def _is_visible(self):
        """ Check if this index is currently visible """
        #: TODO
        return True
        #d = self.table.declaration
        #return self.declaration.row
    
    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.table.model.dataChanged.emit(self.index,self.index)
                
        
class QtTableViewRow(AbstractQtTableViewItemGroup, ProxyTableViewRow):
    pass
            
class QtTableViewColumn(AbstractQtTableViewItemGroup, ProxyTableViewColumn):
    pass
