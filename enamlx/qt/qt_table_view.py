# -*- coding: utf-8 -*-
'''
Created on Aug 28, 2015

@author: jrm
'''
from enaml.application import timed_call
from enaml.qt.q_resource_helpers import get_cached_qicon, get_cached_qcolor
from atom.api import Typed,Instance,Int,ContainerList,observe
from enamlx.qt.qt_abstract_item_view import QtAbstractItemView
from enamlx.widgets.table_view import ProxyTableViewItem,ProxyTableView,ProxyTableViewColumn,ProxyTableViewRow
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem,AbstractQtWidgetItemGroup,\
    TEXT_H_ALIGNMENTS, TEXT_V_ALIGNMENTS,RESIZE_MODES
from enaml.qt.QtGui import QTableView
from enaml.qt.QtCore import Qt,QAbstractTableModel,QModelIndex,QPoint




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
        d = self.view.declaration
        if d.iterable:
            return len(d.iterable)
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
        #elif role == Qt.SizeHintRole and d.width:
        #    return 
        return None
    
    def itemAt(self,index):
        if not index.isValid():
            return None
        self.view.visible_index = index
        self.view.current_index = self.view.widget.currentIndex()
        d = self.view.declaration
        #if index.row()+d.prefetch_size>len(self.items): # prefetch
        #    self.fetchMore(index)
        i = max(0,index.row()-d.iterable_index)
        try:
            return self.items[i][index.column()]
        except IndexError:
            return None
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[col] # For now...
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col
        return None

#     def canFetchMore(self, index):
#         return len(self.items)<len(self.view.declaration.iterable)
#     
#     def fetchMore(self, index):
#         d = self.view.declaration
#         r = index.row() if index.isValid() else len(self.items)
#         print("Fetch more row=%s!"%r)
#         d.iterable_index = r # Foreces window to load more


class QtTableView(QtAbstractItemView, ProxyTableView):
    widget = Typed(QTableView)
    
    # Model used by the table view 
    # Simply takes data from the declaration
    model = Instance(QAtomTableModel) 
    
    # Contains the headers
    headers = ContainerList(default=[])
    
    # Contains all the rows
    items = ContainerList(default=[])
    
    current_index = Instance(QModelIndex)
    visible_index = Instance(QModelIndex) # Last updated index
    
    # Refreshing the view on every update makes it really slow
    # So if we defer refreshing until everything is added it's fast :) 
    _pending_refreshes = Int(0)
    
    def create_widget(self):
        self.widget = QTableView(self.parent_widget())
        self.model = QAtomTableModel(view=self,parent=self.widget)
        #loading = TableViewItem(text='',tool_tip='loading',proxy=ProxyTableViewItem())
        #self.items = [[] for i in range(len(self.declaration.iterable))]
        
    def init_widget(self):
        super(QtTableView, self).init_widget()
        d = self.declaration
        self.set_model(self.model)
        self.set_show_grid(d.show_grid)
        self.set_word_wrap(d.word_wrap)
        self.set_show_vertical_header(d.show_vertical_header)
        self.set_show_horizontal_header(d.show_horizontal_header)
        self.set_horizontal_stretch(d.horizontal_stretch)
        self.set_vertical_stretch(d.vertical_stretch)
        self.set_resize_mode(d.resize_mode)
        self.set_current_row(d.current_row)
        self.set_current_column(d.current_column)
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
        for child in self.rows():
            self.child_added(child)
     
     
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
            header = self.widget.horizontalHeader()
            
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
    
    def set_model(self,model):
        self.widget.setModel(model)
        
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
                item.model_index = self.model.index(x,y)
                if item.delegate:
                    self.widget.setIndexWidget(item.model_index,item.delegate.widget)
                
            self.items.append(child)
            #print("Added %s"%len(self.items))
            
            
    def child_removed(self, child):
        """  Handle the child removed event for a QtTableView."""
        if isinstance(child,(QtTableViewColumn,QtTableViewRow)):
            self.items.remove(child)
            pass
        
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
        #if change['name']=='width':
        #    return self.set_width(change['value'])
        parent = self.parent().parent()
        parent.model.dataChanged.emit(self.model_index,self.model_index)
    
        
class QtTableViewRow(AbstractQtTableViewItemGroup, ProxyTableViewRow):
    pass


class QtTableViewColumn(AbstractQtTableViewItemGroup, ProxyTableViewColumn):
    pass
