# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: jrm
'''
from atom.api import Typed,Instance
from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.table_widget import ProxyTableWidgetItem,ProxyTableWidget,ProxyTableWidgetColumn,ProxyTableWidgetRow
from enaml.qt.QtGui import QIcon,QTableWidget,QTableWidgetItem,QSizePolicy
from enaml.qt.QtCore import Qt,QSize
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_widget import QtWidget
from enaml.core.pattern import Pattern
from enaml.qt.q_resource_helpers import get_cached_qicon
from functools import wraps

def except_delegate(f):
    @wraps(f)
    def wrapped(self,*args,**kwargs):
        if self.delegate is not None:
            return 
        return f(self,*args,**kwargs)
    return wrapped

class QtTableWidget(QtAbstractItemView, ProxyTableWidget):
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
        self.init_signals()
        
    def init_signals(self):
        """ Connect signals """
        self.widget.itemPressed.connect(self.on_item_pressed)
        self.widget.itemActivated.connect(self.on_item_activated)
        self.widget.itemChanged.connect(self.on_item_changed)
        self.widget.itemClicked.connect(self.on_item_clicked)
        self.widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.widget.itemEntered.connect(self.on_item_entered)
        self.widget.itemPressed.connect(self.on_item_pressed)
        self.widget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.widget.currentCellChanged.connect(self.on_current_cell_changed)
         
    def init_layout(self):
        for child in self.rows():
            self.child_added(child)
            
    def _refresh_layout(self):
        super(QtTableWidget, self)._refresh_layout()
        self.set_headers(self.declaration.headers)
        self.set_auto_resize_columns(self.declaration.auto_resize_columns)
            
    def set_sortable(self,sortable):
        self.widget.setSortingEnabled(sortable)
        
    def set_headers(self,headers):
        self.widget.setHorizontalHeaderLabels(headers)
        
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
    
    def rows(self):
        return [child for child in self.children() if isinstance(child, QtTableWidgetRow)]
    
    def columns(self):
        return [child for child in self.children() if isinstance(child, QtTableWidgetColumn)]
    
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def on_item_activated(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_activated()
        
    def on_item_clicked(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_clicked()
        
    def on_item_double_clicked(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_double_clicked()
    
    def on_item_pressed(self,item):
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_pressed()
    
    def on_item_changed(self,item):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_changed()
        
    def on_item_entered(self,item):    
        """ Delegate event handling to the proxy """
        item._proxy_ref.on_item_entered()
        
    def on_item_selection_changed(self):    
        """ Delegate event handling to the proxy """
        for child in self.children():
            if isinstance(child,AbstractQtTableWidgetItem):
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


class AbstractQtTableWidgetItem(QtControl):
    
    def create_widget(self):
        pass
    
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
                
    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_item_activated(self):
        self.declaration.activated()
    
    def on_item_clicked(self):
        self.declaration.clicked()
        self.on_item_checked()
        
    def on_item_double_clicked(self):
        self.declaration.double_clicked()
    
    def on_item_pressed(self):    
        self.declaration.pressed()
        self.on_item_checked()
    
    def on_item_changed(self):    
        self.declaration.changed()
        
    def on_item_entered(self):    
        self.declaration.entered()
        
    def on_item_selection_changed(self):
        for child in self.children():
            if isinstance(child, QtTableWidgetItem):
                child.on_item_selection_changed()
        selected = self._is_selected()
        if selected != self.declaration.selected:
            self.declaration.selected = selected
            self.declaration.selection_changed(selected)
        
    def on_item_checked(self):
        checked = self._is_checked()
        if checked!=self.declaration.checked:   
            self.declaration.checked = checked 
            self.declaration.toggled(checked)
    
    def _is_selected(self):
        for child in self.children():
            if isinstance(child, AbstractQtTableWidgetItem) and child._is_selected():
                return True
        return False
    
    def _is_checked(self):
        for child in self.children():
            if isinstance(child, AbstractQtTableWidgetItem) and child._is_checked():
                return True
        return False


class QtTableWidgetItem(AbstractQtTableWidgetItem, ProxyTableWidgetItem):
    widget = Instance((QTableWidget,QTableWidgetItem))
    delegate = Instance(QtWidget)

    def create_widget(self):
        for child in self.children():
            if isinstance(child,(Pattern,QtWidget)):
                self.delegate = child
        
        if self.delegate:
            self.widget = self.parent_widget()
        else:
            self.widget = QTableWidgetItem()            
            # Save a reference to the proxy 
            self.widget._proxy_ref = self
        
    def __repr__(self):
        return "QtTableWidgetItem(row=%s,col=%s,text=%s)"%(self.declaration.row,self.declaration.column,self.declaration.text)
        
    def init_widget(self):
        d = self.declaration
        self.set_selectable(d.selectable)
        self.set_editable(d.editable)
        self.set_checkable(d.checkable)
        if d.checkable:
            self.set_checked(d.checked)
        if d.selectable:
            self.set_selected(d.selected)
        if d.text:
            self.set_text(d.text)
        if d.icon:
            self.set_icon(d.icon)
        if -1 not in d.icon_size:
            self.set_icon_size(d.icon_size)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
     
    @except_delegate   
    def set_tool_tip(self, tool_tip):
        self.widget.setData(Qt.ToolTipRole,tool_tip)
    
    @except_delegate
    def set_checked(self, checked):
        checked = checked and Qt.CheckState.Checked or Qt.CheckState.Unchecked
        self.widget.setCheckState(checked)
        
    @except_delegate
    def set_icon(self,icon):
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        self.widget.setIcon(qicon)
        
    @except_delegate
    def set_icon_size(self, size):
        self.widget.setIconSize(QSize(*size))
    
    @except_delegate
    def set_selected(self, selected):
        self.widget.setSelected(selected)
    
    @except_delegate
    def set_text(self, text):
        self.widget.setText(text)
    
    @except_delegate
    def set_text_alignment(self, alignment):
        self.widget.setTextAlignment(alignment)
    
    @except_delegate    
    def set_checkable(self, checkable):
        flags = self.widget.flags()
        if checkable:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        else:
            flags &= ~Qt.ItemFlag.ItemIsUserCheckable
        self.widget.setFlags(flags)
    
    @except_delegate    
    def set_selectable(self, selectable):
        flags = self.widget.flags()
        if selectable:
            flags |= Qt.ItemFlag.ItemIsSelectable
        else:
            flags &= ~Qt.ItemFlag.ItemIsSelectable
        self.widget.setFlags(flags)
    
    @except_delegate    
    def set_editable(self, editable):
        flags = self.widget.flags()
        if editable:
            flags |= Qt.ItemFlag.ItemIsEditable
        else:
            flags &= ~Qt.ItemFlag.ItemIsEditable
        self.widget.setFlags(flags)
    
    @except_delegate
    def set_flags(self, flags):
        """
        Qt.NoItemFlags          0   It does not have any properties set.
        Qt.ItemIsSelectable     1   It can be selected.
        Qt.ItemIsEditable       2   It can be edited.
        Qt.ItemIsDragEnabled    4   It can be dragged.
        Qt.ItemIsDropEnabled    8   It can be used as a drop target.
        Qt.ItemIsUserCheckable  16  It can be checked or unchecked by the user.
        Qt.ItemIsEnabled        32  The user can interact with the item.
        Qt.ItemIsTristate       64  The item is checkable with three separate states.
        
        """
        self.widget.setFlags(flags)
    
    def set_row(self, row):
        pass
        
    def set_column(self, column):
        pass
        
    def _is_selected(self):
        return self.widget.isSelected()
    
    def _is_checked(self):
        return self.widget.checkState() == Qt.CheckState.Checked
    
    def on_item_selection_changed(self):
        selected = self._is_selected()
        if selected != self.declaration.selected:
            self.declaration.selected = selected
            self.declaration.selection_changed(selected)
        
    def destroy(self):
        """ For some reason it can't use this... """
        self.widget = None
        super(QtTableWidgetItem, self).destroy()
        
class QtTableWidgetRow(AbstractQtTableWidgetItem, ProxyTableWidgetRow):
    
    @property
    def widget(self):
        return self.parent_widget()
    
    def on_item_selection_changed(self):
        super(QtTableWidgetRow, self).on_item_selection_changed()
        for child in self.items():
            if isinstance(child, QtTableWidgetItem):
                child.on_item_changed()
                
            
    def items(self):
        return [child for child in self.children() if isinstance(child, QtTableWidgetItem)]
            


class QtTableWidgetColumn(AbstractQtTableWidgetItem, ProxyTableWidgetColumn):
    
    @property
    def widget(self):
        return self.parent_widget()
    
    def on_item_selection_changed(self):
        super(QtTableWidgetRow, self).on_item_selection_changed()
        for child in self.items():
            if isinstance(child, QtTableWidgetItem):
                child.on_item_changed()
                
    def items(self):
        return [child for child in self.children() if isinstance(child, QtTableWidgetItem)]

