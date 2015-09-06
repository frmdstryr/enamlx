# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: jrm
'''
from atom.api import Typed,Instance
from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.table_widget import ProxyTableWidgetItem,ProxyTableWidget,ProxyTableWidgetColumn,ProxyTableWidgetRow
from enaml.qt.QtGui import QTableWidget,QTableWidgetItem,QSizePolicy
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,\
    AbstractQtWidgetItemGroup, RESIZE_MODES
from enaml.widgets.menu import Menu
from enaml.qt.qt_menu import QtMenu


class QtTableWidget(QtAbstractItemView, ProxyTableWidget):
    """ DO NOT USE THIS FOR TABLES WITH > ~300 rows """
    widget = Typed(QTableWidget)
    
    def create_widget(self):
        self.widget = QTableWidget(self.parent_widget())
        
    def init_widget(self):
        super(QtTableWidget, self).init_widget()
        d = self.declaration
        self.widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.set_show_grid(d.show_grid)
        self.set_word_wrap(d.word_wrap)
        self.set_show_vertical_header(d.show_vertical_header)
        self.set_show_horizontal_header(d.show_horizontal_header)
        self.set_horizontal_stretch(d.horizontal_stretch)
        self.set_vertical_stretch(d.vertical_stretch)
        self.set_resize_mode(d.resize_mode)
        if d.vertical_minimum_section_size:
            self.set_vertical_minimum_section_size(d.vertical_minimum_section_size)
        if d.horizontal_minimum_section_size:
            self.set_horizontal_minimum_section_size(d.horizontal_minimum_section_size)
        
    
    def init_signals(self):
#         self.widget.itemActivated.connect(self.on_item_activated)
#         self.widget.itemClicked.connect(self.on_item_clicked)
#         self.widget.itemDoubleClicked.connect(self.on_item_double_clicked)
#         self.widget.itemEntered.connect(self.on_item_entered)
#         self.widget.itemPressed.connect(self.on_item_pressed)
#         self.widget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)
#         
        super(QtTableWidget, self).init_signals()
        self.widget.itemChanged.connect(self.on_item_changed)
        self.widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.widget.currentCellChanged.connect(self.on_current_cell_changed)
         
    def init_layout(self):
        self.widget.blockSignals(True)
        for child in self.rows():
            self.child_added(child)
        self.widget.blockSignals(False)
            
    def _refresh_layout(self):
        super(QtTableWidget, self)._refresh_layout()
        self.set_headers(self.declaration.headers)
        #self.set_auto_resize_columns(self.declaration.auto_resize_columns)
            
    def set_sortable(self,sortable):
        self.widget.setSortingEnabled(sortable)
        
    def set_headers(self,headers):
        self.widget.setHorizontalHeaderLabels(headers)
        
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
    
    def set_padding(self,padding):
        self.widget.setStyleSheet("QTableWidget::item { padding: %ipx }"%padding);
    
    def set_resize_mode(self,mode):
        self.widget.horizontalHeader().setResizeMode(RESIZE_MODES[mode])
    
    def set_show_horizontal_header(self,show):
        header = self.widget.horizontalHeader()
        header.show() if show else header.hide()
        
    def set_show_vertical_header(self,show):
        header = self.widget.verticalHeader()
        header.show() if show else header.hide()
            
    def set_auto_resize_columns(self,enabled):
        if enabled:
            self.widget.resizeColumnsToContents()
            
    def set_current_row(self,row):
        self.widget.setCurrentCell(row,self.declaration.current_column)
    
    def set_current_column(self,column):
        self.widget.setCurrentCell(self.declaration.current_row,column)
    
    def rows(self):
        return [child for child in self.children() if isinstance(child, QtTableWidgetRow)]
    
    def columns(self):
        return [child for child in self.children() if isinstance(child, QtTableWidgetColumn)]
    
    
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def item_at(self,index):
        if not index.isValid():
            return
        item = self.widget.item(index.row(),index.column())
        return item._proxy_ref
    
    def _check_item_toggled(self, item):
        checked = item.is_checked()
        if checked!=item.declaration.checked:
            item.parent().declaration.checked = checked 
            item.parent().declaration.toggled(checked)   
            item.declaration.checked = checked 
            item.declaration.toggled(checked)
    
    def on_item_selection_changed(self):    
        """ Delegate event handling to the proxy """
        for child in self.children():
            if isinstance(child,AbstractQtWidgetItemGroup):
                child.on_item_selection_changed()
    
    def on_item_changed(self,item):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_changed()
        
    def on_item_selection_changed(self):    
        """ Delegate event handling to the proxy """
        for child in self.children():
            if isinstance(child,AbstractQtWidgetItemGroup):
                child.on_item_selection_changed()

    
    def on_current_cell_changed(self):    
        """ Delegate event handling to the proxy """
        self.declaration.current_row = self.widget.currentRow()
        self.declaration.current_column = self.widget.currentColumn()
    
    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtTableWidget."""
        if isinstance(child, QtTableWidgetRow):
            row = self.rows().index(child)
            child.set_row(row)
            
            if row>=self.widget.rowCount():
                self.widget.insertRow(child.declaration.row)
            
            for column,item in enumerate(child.items()):
                if column>=self.widget.columnCount():
                    self.widget.insertColumn(column)
                if item.delegate is not None:
                    self.widget.setCellWidget(item.declaration.row,item.declaration.column,item.delegate.widget)
                else:
                    self.widget.setItem(item.declaration.row,item.declaration.column,item.widget)
        
        elif isinstance(child, QtTableWidgetColumn):
            column = self.coluns().index(child)
            child.set_columns(column)
            
            if column>=self.widget.columnCount():
                self.widget.insertColumn(child.declaration.column)
                
            for row,item in enumerate(child.items()):
                if row>=self.widget.rowCount():
                    self.widget.insertRow(row)
                if item.delegate is not None:
                    self.widget.setCellWidget(item.declaration.row,item.declaration.column,item.delegate.widget)
                else:
                    self.widget.setItem(item.declaration.row,item.declaration.column,item.widget)
        
        elif isinstance(child, QtTableWidgetItem):
            if child.delegate is not None:
                self.widget.setCellWidget(child.declaration.row,child.declaration.column,child.widget)
            else:
                self.widget.setItem(child.declaration.row,child.declaration.column,child.widget)
        
        self._refresh_layout()

    def child_removed(self, child):
        """  Handle the child removed event for a QtTableWidget."""
        if isinstance(child, QtTableWidgetRow):
            for item in self.rows():
                if item.declaration.row>=child.declaration.row:
                    item.declaration.row -=1
            self.widget.removeRow(child.declaration.row)     
        elif isinstance(child, QtTableWidgetColumn):
            for item in self.columns():
                if item.declaration.column>=child.declaration.column:
                    item.declaration.column -=1
            self.widget.removeColumn(child.declaration.column)
        elif isinstance(child, QtTableWidgetItem):
            self.widget.removeCellWidget(child.declaration.row,child.declaration.column)
            
        self._refresh_layout()
        
    def destroy(self):
        """ Will crash on close if this is not done """
        self.widget.clearContents()
        super(QtTableWidget, self).destroy()


class AbstractQtTableWidgetItemGroup(AbstractQtWidgetItemGroup):
    
    def create_widget(self):
        pass
    
    @property
    def widget(self):
        return self.parent_widget()
    
    @property
    def is_destroyed(self):
        return True
    
    
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
                

class QtTableWidgetItem(AbstractQtWidgetItem, ProxyTableWidgetItem):
    widget = Instance((QTableWidget,QTableWidgetItem))

    def create_widget(self):
        super(QtTableWidgetItem, self).create_widget()
        if not self.delegate:
            self.widget = QTableWidgetItem()            
            # Save a reference to the proxy 
            self.widget._proxy_ref = self
            
    def activate_top_down(self):
        #print("activate top down %s"%([c for c in self.children()],))
        for child in self.children():
            if isinstance(child, QtMenu):
                # Move it to the parent and wrap it in a conditional 
                child.declaration._parent = self.parent()
        super(QtTableWidgetItem, self).activate_top_down()
        
    def __repr__(self):
        return "QtTableWidgetItem(row=%s,col=%s,text=%s)"%(self.declaration.row,self.declaration.column,self.declaration.text)
        
    def set_row(self, row):
        pass
        
    def set_column(self, column):
        pass
    
class QtTableWidgetRow(AbstractQtTableWidgetItemGroup, ProxyTableWidgetRow):
    pass

class QtTableWidgetColumn(AbstractQtTableWidgetItemGroup, ProxyTableWidgetColumn):
    pass