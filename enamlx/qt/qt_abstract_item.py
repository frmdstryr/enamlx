# -*- coding: utf-8 -*-
'''
Created on Aug 24, 2015

@author: jrm
'''
from atom.api import Instance
from enaml.core.pattern import Pattern
from enaml.qt.q_resource_helpers import get_cached_qicon
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_widget import QtWidget
from enaml.qt.QtGui import QAbstractItemView
from enaml.qt.QtGui import QIcon
from enaml.qt.QtCore import Qt,QSize

from functools import wraps

TEXT_H_ALIGNMENTS = {
    'left':0x01,#Qt.AlignLeft,
    'right':0x02, #Qt.AlignRight,
    'center':0x04, #Qt.AlignHCenter,
    'justify':0x08,#Qt.AlignJustify,
}

TEXT_V_ALIGNMENTS = {
    'top':0x20,#Qt.AlignTop,
    'bottom':0x40,#Qt.AlignBottom,
    'center':0x80,#Qt.AlignVCenter,
}

def except_delegate(f):
    """ Only calls the function if control is not
    delegated to a child widget. """
    @wraps(f)
    def wrapped(self,*args,**kwargs):
        if self.delegate is not None:
            return 
        return f(self,*args,**kwargs)
    return wrapped

class AbstractQtWidgetItemGroup(QtControl):
    
    def refresh_style_sheet(self):
        pass # Takes a lot of time
    
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
    
    def on_item_entered(self):    
        self.declaration.entered()
        
    def on_item_changed(self):    
        self.declaration.changed()
        
    def on_item_selection_changed(self):
        for item in self.items():
            item.on_item_selection_changed()
        selected = self.is_selected()
        if selected != self.declaration.selected:
            self.declaration.selected = selected
            self.declaration.selection_changed(selected)
            
    def is_selected(self):
        for item in self.items():
            if item.is_selected():
                return True
        return False
    
    def is_checked(self):
        for item in self.items():
            if item.is_checked():
                return True
        return False
        
    def items(self):
        # TODO: Cache these as it's slow!
        return [it for it in self]
    
    def __iter__(self):
        for c in self.children():
            if isinstance(c,AbstractQtWidgetItem):
                yield c

    def __getitem__(self,key):
        try:
            return self.items()[key]
        except IndexError:
            return None
        
    
class AbstractQtWidgetItem(AbstractQtWidgetItemGroup):
    widget = Instance(QAbstractItemView)
    delegate = Instance(QtWidget)
    
    def create_widget(self):
        for child in self.children():
            if isinstance(child,(Pattern,QtWidget)):
                self.delegate = child
        
        if self.delegate:
            self.widget = self.parent_widget()
            
    @property
    def view_widget(self):
        parent = self
        widget = parent.parent_widget()
        while not isinstance(widget,QAbstractItemView):
            parent = parent.parent()
            widget = parent.parent_widget()
        return widget
    
        
    def init_widget(self):
        #super(AbstractQtWidgetItem, self).init_widget()
        self.declaration.column = self.parent().items().index(self)
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
        if d.width:
            self.set_width(d.width)
        if d.text_alignment:
            self.set_text_alignment(d.text_alignment)
    
    def set_width(self,width):
        #print('width=%s,col=%s'%(width,self.declaration.column))
        self.view_widget.setColumnWidth(self.declaration.column,width)
    
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
        h,v = alignment
        self.widget.setTextAlignment(TEXT_H_ALIGNMENTS[h] | TEXT_V_ALIGNMENTS[v])
    
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
    
    def on_item_selection_changed(self):
        selected = self.is_selected()
        if selected != self.declaration.selected:
            self.declaration.selected = selected
            self.declaration.selection_changed(selected)
            
    def on_item_checked(self):
        checked = self.is_checked()
        if checked!=self.declaration.checked:   
            self.declaration.checked = checked 
            self.declaration.toggled(checked)
    
    @except_delegate
    def is_selected(self):
        return self.widget.isSelected()
    
    @except_delegate
    def is_checked(self):
        return self.widget.checkState() == Qt.CheckState.Checked
    
    def destroy(self):
        """ WidgetItems are not QtWidgets and cannot be destroyed, 
            they must be cleaned up by the parent view.  """
        self.widget = None # Destroyed by parent
        super(AbstractQtWidgetItem, self).destroy()
    
    
    