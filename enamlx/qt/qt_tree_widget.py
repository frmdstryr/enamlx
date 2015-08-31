# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: jrm
'''
from atom.api import Typed,Instance
from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.tree_widget import ProxyTreeWidgetItem,ProxyTreeWidget#,ProxyTreeWidgetColumn,ProxyTreeWidgetRow
from enaml.qt.QtCore import Qt,QSize
from enaml.qt.QtGui import QTreeWidget,QTreeWidgetItem,QIcon
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,\
    AbstractQtWidgetItemGroup, except_delegate, TEXT_H_ALIGNMENTS,\
    TEXT_V_ALIGNMENTS
from atom.property import cached_property
from enaml.core.pattern import Pattern
from enaml.qt.qt_widget import QtWidget
from enaml.qt.q_resource_helpers import get_cached_qicon


class QtTreeWidget(QtAbstractItemView, ProxyTreeWidget):
    widget = Typed(QTreeWidget)
    
    def create_widget(self):
        self.widget = QTreeWidget(self.parent_widget())

    def init_widget(self):
        super(QtTreeWidget, self).init_widget()
        d = self.declaration
        self.set_word_wrap(d.word_wrap)
        #self.set_show_vertical_header(d.show_vertical_header)
        #self.set_show_horizontal_header(d.show_horizontal_header)
        #self.set_horizontal_stretch(d.horizontal_stretch)
        #self.set_vertical_stretch(d.vertical_stretch)
    
    def init_signals(self):
        super(QtTreeWidget, self).init_signals()
        self.widget.itemChanged.connect(self.on_item_changed)
        self.widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.widget.itemExpanded.connect(self.on_item_expanded)
        self.widget.itemCollapsed.connect(self.on_item_collapsed)
         
    def init_layout(self):
        for child in self.children():
            self.child_added(child)
            
    def _refresh_layout(self):
        super(QtTreeWidget, self)._refresh_layout()
        self.set_headers(self.declaration.headers)
        #self.set_auto_resize_columns(self.declaration.auto_resize_columns)
        
    def items(self):
        return [c for c in self.children() if isinstance(c,QtTreeWidgetItem)]
            
    def set_sortable(self,sortable):
        self.widget.setSortingEnabled(sortable)
        
    def set_headers(self,headers):
        self.widget.setHeaderLabels(headers)
        
    def set_show_grid(self,show):
        self.widget.setShowGrid(show)
        
    def set_word_wrap(self,wrap):
        self.widget.setWordWrap(wrap)
        
    def set_horizontal_stretch(self,stretch):
        self.widget.horizontalHeader().setStretchLastSection(stretch)
        
    def set_vertical_stretch(self,stretch):
        self.widget.verticalHeader().setStretchLastSection(stretch)
    
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
    
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def on_current_cell_changed(self):    
        """ Delegate event handling to the proxy """
        self.declaration.current_row = self.widget.currentRow()
        self.declaration.current_column = self.widget.currentColumn()
    
    def on_item_expanded(self,item):
        pass
    
    def on_item_collapsed(self,item):
        pass
    
        #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def on_item_activated(self,item,index):
        """ Delegate event handling to the proxy """
        item._proxy_ref.columns()[index].on_item_activated()
        
    def on_item_clicked(self,item,index):
        """ Delegate event handling to the proxy """
        item._proxy_ref.columns()[index].on_item_clicked()
        
    def on_item_double_clicked(self,item,index):
        """ Delegate event handling to the proxy """
        item._proxy_ref.columns()[index].on_item_double_clicked()
    
    def on_item_pressed(self,item,index):
        """ Delegate event handling to the proxy """
        item._proxy_ref.columns()[index].on_item_pressed()
    
    def on_item_changed(self,item,index):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.columns()[index].on_item_changed()
        
    def on_item_entered(self,item,index):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.columns()[index].on_item_entered()
    
    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtTreeWidget."""
        if isinstance(child, QtTreeWidgetItem):
            self.widget.insertTopLevelItem(child.declaration.row,child.widget)
            if child.delegate:
                self.widget.setItemWidget(child.item,child.declaration.column,child.delegate.widget)
            for item in child.children():
                if isinstance(item, QtTreeWidgetItemColumn):
                    if item.delegate:
                        self.widget.setItemWidget(child.widget,item.declaration.column,item.delegate.widget)
                elif isinstance(item, QtTreeWidgetItem):
                    child.widget.addChild(item.widget)
        
        self._refresh_layout()

    def child_removed(self, child):
        """  Handle the child removed event for a QtTreeWidget."""
        if isinstance(child, QtTreeWidgetItem):
            self.widget.takeTopLevelItem(child.declaration.row)
            
        self._refresh_layout()


class AbstractQtTreeWidgetItemGroup(AbstractQtWidgetItemGroup):
    
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
                

class QtTreeWidgetItem(AbstractQtWidgetItem, ProxyTreeWidgetItem):
    widget = Instance((QTreeWidget,QTreeWidgetItem))
    item = Instance(QTreeWidgetItem)
    
    
    def create_widget(self):
        self.widget = QTreeWidgetItem()            
        # Save a reference to the proxy 
        self.widget._proxy_ref = self
        
    def __repr__(self):
        return "QtTreeWidgetItem(row=%s,col=%s,text=%s)"%(self.declaration.row,self.declaration.column,self.declaration.text)
    
    def _default_column(self):
        parent = self.parent()
        if isinstance(parent, QtTreeWidget):
            return 0
        return self.parent().items().index(self)
    
    def items(self):
        return [c for c in self.children() if isinstance(c, QtTreeWidgetItem) and not isinstance(c, QtTreeWidgetItemColumn)]
        
    def set_row(self, row):
        pass
        
    @except_delegate
    def set_text(self, text):
        self.widget.setText(self.declaration.column,text)
        
    @except_delegate
    def set_text_alignment(self, alignment):
        h,v = alignment
        self.widget.setTextAlignment(self.declaration.column,TEXT_H_ALIGNMENTS[h] | TEXT_V_ALIGNMENTS[v])
    
    @except_delegate
    def set_checked(self, checked):
        checked = checked and Qt.Checked or Qt.Unchecked
        self.widget.setCheckState(self.declaration.column,checked)
        
    @except_delegate
    def set_tool_tip(self, tool_tip):
        self.widget.setData(self.declaration.column,Qt.ToolTipRole,tool_tip)
    
    @except_delegate 
    def set_icon(self,icon):
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        self.widget.setIcon(self.declaration.column,qicon)
    
    @except_delegate
    def set_icon_size(self, size):
        self.widget.setIconSize(self.declaration.column,QSize(*size))
    
    @except_delegate
    def set_selected(self, selected):
        self.widget.setSelected(self.declaration.column,selected)
        
    @except_delegate
    def is_checked(self):
        return self.widget.checkState(self.declaration.column) == Qt.Checked
        
    def columns(self):
        """ Return columns of this child with self being the first column """
        return [self]+[c for c in self.children() if isinstance(c,QtTreeWidgetItemColumn)]

class QtTreeWidgetItemColumn(QtTreeWidgetItem):
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child
        if self.delegate:
            self.widget = self.parent_widget().treeWidget()
        else:
            self.widget = self.parent_widget()
            
    def _default_column(self):
        return self.parent().columns().index(self)
        
    def columns(self):
        return []
    

    
    
