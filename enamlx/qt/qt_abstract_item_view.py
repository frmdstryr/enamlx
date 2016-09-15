# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2015

@author: jrm
'''
from atom.api import Instance, Int, observe
from enaml.application import timed_call
from enaml.qt.qt_control import QtControl
from enaml.qt.QtGui import QAbstractItemView, QItemSelectionModel
from enaml.qt.QtCore import Qt, QAbstractItemModel
from enaml.qt.q_resource_helpers import get_cached_qicon, get_cached_qcolor

from enamlx.qt.qt_abstract_item import (
    RESIZE_MODES, TEXT_H_ALIGNMENTS, TEXT_V_ALIGNMENTS
)
from enamlx.widgets.abstract_item_view import ProxyAbstractItemView


SELECTION_MODES = {
    'extended':QAbstractItemView.ExtendedSelection,
    'single':QAbstractItemView.SingleSelection,
    'contiguous':QAbstractItemView.ContiguousSelection,
    'multi':QAbstractItemView.MultiSelection,
    'none':QAbstractItemView.NoSelection,
}

SELECTION_BEHAVIORS = {
    'items':QAbstractItemView.SelectItems,
    'rows':QAbstractItemView.SelectRows,
    'columns':QAbstractItemView.SelectColumns,
}

class QAbstractAtomItemModel(object):
    
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
        return super(QAbstractAtomItemModel, self).setData(index, value, role)
    
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

class QtAbstractItemView(QtControl, ProxyAbstractItemView):
    widget = Instance(QAbstractItemView)
    
    #: View model
    model = Instance(QAbstractItemModel)
    
    #: Hold reference to selection model to PySide segfault
    selection_model = Instance(QItemSelectionModel)
    
    #: Refreshing the view on every update makes it really slow
    #: So if we defer refreshing until everything is added it's fast :) 
    _pending_view_refreshes = Int(0)
    _pending_row_refreshes = Int(0)
    _pending_col_refreshes = Int(0)
    
    def init_widget(self):
        super(QtAbstractItemView, self).init_widget()
        
        self.init_model()
        
        d = self.declaration
        
        #: Enable context menus
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.set_selection_mode(d.selection_mode)
        self.set_selection_behavior(d.selection_behavior)
        self.set_alternating_row_colors(d.alternating_row_colors)
        self.set_show_grid(d.show_grid)
        self.set_word_wrap(d.word_wrap)
        self.set_resize_mode(d.resize_mode)
        self.set_show_vertical_header(d.show_vertical_header)
        self.set_show_horizontal_header(d.show_horizontal_header)
        self.set_horizontal_stretch(d.horizontal_stretch)
        self.set_vertical_stretch(d.vertical_stretch)
        if d.cell_padding:
            self.set_cell_padding(d.cell_padding)
        if d.vertical_minimum_section_size:
            self.set_vertical_minimum_section_size(d.vertical_minimum_section_size)
        if d.horizontal_minimum_section_size:
            self.set_horizontal_minimum_section_size(d.horizontal_minimum_section_size)
        
        self.init_signals()

    def init_model(self):
        raise NotImplementedError

    def init_signals(self):
        """ Connect signals """
        self.widget.activated.connect(self.on_item_activated)
        self.widget.clicked.connect(self.on_item_clicked)
        self.widget.doubleClicked.connect(self.on_item_double_clicked)
        self.widget.entered.connect(self.on_item_entered)
        self.widget.pressed.connect(self.on_item_pressed)
        self.widget.customContextMenuRequested.connect(self.on_custom_context_menu_requested)
        self.selection_model = self.widget.selectionModel()
        self.selection_model.selectionChanged.connect(self.on_selection_changed)
        self.widget.horizontalScrollBar().valueChanged.connect(self.on_horizontal_scrollbar_moved)
        self.widget.verticalScrollBar().valueChanged.connect(self.on_vertical_scrollbar_moved)
    
    def item_at(self,index):
        if not index.isValid():
            return
        return self.model.itemAt(index)
    
    def destroy(self):
        """ Make sure all the table widgets are destroyed first."""
        self.model.clear()
        super(QtAbstractItemView, self).destroy()
    
    #--------------------------------------------------------------------------
    # Widget Setters
    #--------------------------------------------------------------------------
    
    def set_selection_mode(self,mode):
        self.widget.setSelectionMode(SELECTION_MODES[mode])
        
    def set_selection_behavior(self,behavior):
        self.widget.setSelectionBehavior(SELECTION_BEHAVIORS[behavior])
        
    def set_scroll_to_bottom(self,enabled):
        if enabled:
            self.widget.scrollToBottom()
            
    def set_alternating_row_colors(self,enabled):
        self.widget.setAlternatingRowColors(enabled)
        
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
        if enabled:
            self.widget.resizeColumnsToContents()
    
    def set_visible_row(self, row):
        self.widget.verticalScrollBar().setValue(row)
    
    def set_visible_column(self, column):
        self.widget.horizontalScrollBar().setValue(column)
        
    def set_model(self,model):
        if isinstance(model,QAbstractAtomItemModel):
            model.setDeclaration(self.declaration)
        self.widget.setModel(model)
        self.model = self.widget.model()
    
    def set_items(self, items):
        """ Defer until later so the view is only updated after all items
        are added. """
        self._pending_view_refreshes +=1
        timed_call(100,self._refresh_layout)
    
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    
    def on_horizontal_scrollbar_moved(self,value):
        """ When the scrollbar moves, queue a refresh of the visible
            columns.  This makes it only update the view when needed
            making scrolling much smoother.   
        """
        self._pending_column_refreshes +=1
        timed_call(0,self._refresh_visible_column,value)
    
    def on_vertical_scrollbar_moved(self,value):
        """ When the scrollbar moves, queue a refresh of the visible
            rows.  This makes it only update the view when needed
            making scrolling much smoother.   
        """
        self._pending_row_refreshes +=1
        timed_call(0,self._refresh_visible_row,value)
        
    def on_item_activated(self, index):
        item = self.item_at(index)
        if not item:
            return
        item.parent().declaration.activated()
        item.declaration.activated()
        
    def on_item_clicked(self, index):
        item = self.item_at(index)
        if not item:
            return
        item.parent().declaration.clicked()
        item.declaration.clicked()
        
    def on_item_double_clicked(self, index):
        item = self.item_at(index)
        if not item:
            return
        item.parent().declaration.double_clicked()
        item.declaration.double_clicked()
        
    def on_item_pressed(self,index):
        item = self.item_at(index)
        if not item:
            return
        item.parent().declaration.pressed()
        item.declaration.pressed()
    
    def on_item_entered(self,index):
        item = self.item_at(index)
        if not item:
            return
        item.parent().declaration.entered()
        item.declaration.entered()
    
    def on_selection_changed(self,selected,deselected):
        for index in selected.indexes():
            item = self.item_at(index)
            if not item:
                continue
            d = item.declaration
            if d.selected != True:
                d.selected = True
                d.selection_changed(d.selected)

        for index in deselected.indexes():
            item = self.item_at(index)
            if not item:
                continue
            d = item.declaration
            if d.selected != False:
                d.selected = False
                d.selection_changed(d.selected)                
    
    def on_custom_context_menu_requested(self,pos):
        item = self.item_at(self.widget.indexAt(pos))
        if not item:
            return
        
        if item.menu:
            item.menu.popup()
            return
        parent = item.parent()
        if parent and parent.menu:
            parent.menu.popup()
    
    def on_layout_refreshed(self):
        #d = self.declaration
        #self.set_scroll_to_bottom(d.scroll_to_bottom)
        pass
            
    #--------------------------------------------------------------------------
    # View refresh handlers
    #--------------------------------------------------------------------------
    
    def _refresh_layout(self):
        """ Refreshes the layout only when this is the last refresh queued. """
        self._pending_view_refreshes -=1
        if self._pending_view_refreshes==0:
            try:
                self.model.layoutChanged.emit()
                self.on_layout_refreshed()
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

    def _refresh_visible_row(self,value):
        raise NotImplementedError
    
    def _refresh_visible_column(self,value):
        raise NotImplementedError


                                