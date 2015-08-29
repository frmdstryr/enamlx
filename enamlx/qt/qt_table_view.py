# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
# -*- coding: utf-8 -*-
from enaml.qt import QtGui
from enaml.application import timed_call
from enaml.qt.q_resource_helpers import get_cached_qicon, get_cached_qcolor
'''
Created on Aug 20, 2015

@author: jrm
'''
from atom.api import Typed,Instance,Int,ContainerList,observe
from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.table_view import ProxyTableViewItem,ProxyTableView,ProxyTableViewColumn,ProxyTableViewRow
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,AbstractQtWidgetItemGroup,\
    TEXT_H_ALIGNMENTS, TEXT_V_ALIGNMENTS
from enaml.qt.QtGui import QTableView
from enaml.qt.QtCore import Qt,QAbstractTableModel,QModelIndex


class QAtomTableModel(QAbstractTableModel):
    
    def __init__(self,view,*args,**kwargs):
        self.view = view # Link back to the view as we cannot inherit from Atom and QAbstractTableModel
        super(QAtomTableModel, self).__init__(*args,**kwargs)
        
    @property
    def items(self):
        return self.view.items
    
    @property
    def headers(self):
        return self.view.headers
    
    def rowCount(self, parent=None):
        return len(self.items)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
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
        return None
    
    def itemAt(self,index):
        if not index.isValid():
            return None
        return self.items[index.row()][index.column()]
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[col] # For now...
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None


class QtTableView(QtAbstractItemView, ProxyTableView):
    widget = Typed(QTableView)
    
    # Model used by the table view 
    # Simply takes data from the declaration
    model = Instance(QAtomTableModel) 
    
    # Contains the headers
    headers = ContainerList(default=[])
    
    # Contains all the rows
    items = ContainerList(default=[])
    

    # Refreshing the view on every update makes it really slow
    # So if we defer refreshing until everything is added it's fast :) 
    _pending_refreshes = Int(0)
    
    def create_widget(self):
        self.widget = QTableView(self.parent_widget())
        self.model = QAtomTableModel(view=self,parent=self.widget)
        
    @observe('items','headers')
    def _refresh_view(self,change):
        """ Defer until later so the view is only updated after all items
        are added. """
        self._pending_refreshes +=1
        timed_call(200,self._refresh_layout)
        
    def init_widget(self):
        super(QtTableView, self).init_widget()
        d = self.declaration
        #self.widget.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
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
        self.set_headers(d.headers)
    
    def init_signals(self):
        """ Connect signals """
        self.widget.activated.connect(self.on_item_activated)
        self.widget.clicked.connect(self.on_item_clicked)
        self.widget.doubleClicked.connect(self.on_item_double_clicked)
        self.widget.entered.connect(self.on_item_entered)
        self.widget.pressed.connect(self.on_item_pressed)
         
    def init_layout(self):
        self.widget.blockSignals(True)
        for child in self.rows():
            self.child_added(child)
        self.widget.blockSignals(False)
            
    def _refresh_layout(self):
        """ Refreshes the layout only when this is the last refresh queued. """
        if self._pending_refreshes==1:
            self.model.layoutChanged.emit()
        self._pending_refreshes -=1
    
    def _observe_model(self,change):
        self.set_model(change['value'])
        
    def set_model(self,model):
        self.widget.setModel(model)
    
    def set_sortable(self,sortable):
        self.widget.setSortingEnabled(sortable)
        
    def set_headers(self,headers):
        self.headers = headers
        
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
        self.widget.setStyleSheet("QTableView::item { padding: %ipx }"%padding);
    
    def set_resize_mode(self,mode):
        self.widget.horizontalHeader().setResizeMode({
            'interactive':QtGui.QHeaderView.ResizeMode.Interactive,
            'fixed':QtGui.QHeaderView.ResizeMode.Fixed,
            'stretch':QtGui.QHeaderView.ResizeMode.Stretch,
            'resize_to_contents':QtGui.QHeaderView.ResizeMode.ResizeToContents,
            'custom':QtGui.QHeaderView.ResizeMode.Custom
        }[mode])
        
    def set_show_horizontal_header(self,show):
        header = self.widget.horizontalHeader()
        header.show() if show else header.hide()
        
    def set_show_vertical_header(self,show):
        header = self.widget.verticalHeader()
        header.show() if show else header.hide()
            
    def set_auto_resize_columns(self,enabled):
        if enabled:
            self.widget.resizeColumnsToContents()
            
    def set_current_column(self,column):
        self.widget.setCurrentCell(self.declaration.current_row,column)
    
    def rows(self):
        return [child for child in self.children() if isinstance(child, QtTableViewRow)]
    
    def columns(self):
        return [child for child in self.children() if isinstance(child, QtTableViewColumn)]
    
    #--------------------------------------------------------------------------
    # Widget Events
    #--------------------------------------------------------------------------
    def on_item_activated(self, index):
        item = self.model.itemAt(index)
        item.parent().declaration.activated()
        item.declaration.activated()
        
    def on_item_clicked(self, index):
        item = self.model.itemAt(index)
        item.parent().declaration.clicked()
        item.declaration.clicked()
        
    def on_item_double_clicked(self, index):
        item = self.model.itemAt(index)
        item.parent().declaration.double_clicked()
        item.declaration.double_clicked()
        
    def on_item_pressed(self,index):
        item = self.model.itemAt(index)
        item.parent().declaration.pressed()
        item.declaration.pressed()
    
    def on_item_entered(self,index):    
        item = self.model.itemAt(index)
        item.parent().declaration.entered()
        item.declaration.entered()
    
    
    def on_current_cell_changed(self):    
        """ Delegate event handling to the proxy """
        self.declaration.current_row = self.widget.currentRow()
        self.declaration.current_column = self.widget.currentColumn()
    
    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtTableView."""
        if isinstance(child,(QtTableViewColumn,QtTableViewRow)):
            # Update model index for each
            swap = isinstance(child, QtTableViewColumn)
            for i,item in enumerate(child.items()):
                x,y = len(self.items),i
                if swap:
                    x,y = y,x
                item.model_index = self.model.createIndex(x,y)
                
                if item.delegate:
                    self.widget.setIndexWidget(item.model_index,item.delegate.widget)
            
            self.items.append(child)
            
            

    def child_removed(self, child):
        """  Handle the child removed event for a QtTableView."""
        if isinstance(child,(QtTableViewColumn,QtTableViewRow)):
            self.items.remove(child)
        
class AbstractQtTableViewItemGroup(AbstractQtWidgetItemGroup):
    
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
                
                
class QtTableViewItem(AbstractQtWidgetItem, ProxyTableViewItem):
    widget = Instance(QTableView)
    model_index = Instance(QModelIndex)

    def init_widget(self):
        return # do nothing as there is no widget!
        
    def refresh_model(self, change):
        """ Notify the model that data has changed in this cell! """
        parent = self.parent().parent()
        parent.model.dataChanged.emit(self.model_index,self.model_index)
    
        
class QtTableViewRow(AbstractQtTableViewItemGroup, ProxyTableViewRow):
    pass


class QtTableViewColumn(AbstractQtTableViewItemGroup, ProxyTableViewColumn):
    pass
