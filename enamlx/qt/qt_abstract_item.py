# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 24, 2015
"""
from atom.api import Bool, ForwardInstance, Instance
from enaml.core.pattern import Pattern
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_menu import QtMenu
from enaml.qt.qt_widget import QtWidget
from qtpy.QtCore import QModelIndex, Qt
from qtpy.QtWidgets import QHeaderView

from enamlx.widgets.abstract_item import (
    ProxyAbstractWidgetItem,
    ProxyAbstractWidgetItemGroup,
)

TEXT_H_ALIGNMENTS = {
    "left": Qt.AlignLeft,
    "right": Qt.AlignRight,
    "center": Qt.AlignHCenter,
    "justify": Qt.AlignJustify,
}

TEXT_V_ALIGNMENTS = {
    "top": Qt.AlignTop,
    "bottom": Qt.AlignBottom,
    "center": Qt.AlignVCenter,
}

RESIZE_MODES = {
    "interactive": QHeaderView.Interactive,
    "fixed": QHeaderView.Fixed,
    "stretch": QHeaderView.Stretch,
    "resize_to_contents": QHeaderView.ResizeToContents,
    "custom": QHeaderView.Custom,
}


class AbstractQtWidgetItemGroup(QtControl, ProxyAbstractWidgetItemGroup):
    """Base class for Table and Tree Views"""

    #: Context menu for this group
    menu = Instance(QtMenu)

    def init_layout(self):
        for child in self.children():
            if isinstance(child, QtMenu):
                self.menu = child

    def refresh_style_sheet(self):
        pass  # Takes a lot of time


def _abstract_item_view():
    from .qt_abstract_item_view import QtAbstractItemView

    return QtAbstractItemView


class AbstractQtWidgetItem(AbstractQtWidgetItemGroup, ProxyAbstractWidgetItem):
    #:
    is_destroyed = Bool()

    #: Index within the view
    index = Instance(QModelIndex)

    #: Delegate widget to display when editing the cell
    #: if the widget is editable
    delegate = Instance(QtWidget)

    #: Reference to view
    view = ForwardInstance(_abstract_item_view)

    def create_widget(self):
        # View items have no widget!
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child

    def init_widget(self):
        pass

    def init_layout(self):
        super(AbstractQtWidgetItem, self).init_layout()
        self._update_index()

    def _update_index(self):
        """Update where this item is within the model"""
        raise NotImplementedError

    def destroy(self):
        """Set the flag so we know when this item is destroyed"""
        self.is_destroyed = True
        super(AbstractQtWidgetItem, self).destroy()
