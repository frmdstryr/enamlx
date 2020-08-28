# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 28, 2015
"""
from atom.api import (
    Typed, Instance, Property, Int
)
from enamlx.qt.qt_abstract_item_view import (
    QtAbstractItemView, QAbstractAtomItemModel, IS_QT4
)
from enamlx.widgets.tree_view import (
    ProxyTreeViewItem, ProxyTreeView, ProxyTreeViewColumn, AbstractWidgetItem
)
from enamlx.qt.qt_abstract_item import AbstractQtWidgetItem, RESIZE_MODES
from qtpy.QtWidgets import QTreeView
from qtpy.QtCore import QAbstractItemModel, QModelIndex
from enaml.core.pattern import Pattern
from enaml.qt.qt_widget import QtWidget
from enaml.application import timed_call



class QAtomTreeModel(QAbstractAtomItemModel, QAbstractItemModel):

    def rowCount(self, parent):
        d = self.declaration
        if d.vertical_headers:
            return len(d.vertical_headers)
        elif parent.isValid():
            item = parent.internalPointer()
            d = item.declaration
        return len(d.items) if d and not d.is_destroyed else 0

    def columnCount(self, parent):
        d = self.declaration
        if d.horizontal_headers:
            return len(d.horizontal_headers)
        elif parent.isValid():
            item = parent.internalPointer()
            d = item.declaration
        return len(d._columns) if d and not d.is_destroyed else 0

    def index(self, row, column, parent):
        """ The index should point to the corresponding QtControl in the
        enaml object hierarchy.
        """
        item = parent.internalPointer()
        #: If the parent is None
        d = self.declaration if item is None else item.declaration
        if row < len(d._items):
            proxy = d._items[row].proxy
            assert isinstance(proxy, QtTreeViewItem), \
                "Invalid item {}".format(proxy)
        else:
            proxy = d.proxy
        return self.createIndex(row, column, proxy)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if not isinstance(item, QtTreeViewItem) or item.is_destroyed:
            return QModelIndex()
        parent = item.parent()
        if not isinstance(parent, QtTreeViewItem) or parent.is_destroyed:
            return QModelIndex()
        d = parent.declaration
        return self.createIndex(d.row, 0, parent)

    def itemAt(self, index=None):
        if not index or not index.isValid():
            return
        item = index.internalPointer()
        assert isinstance(item, QtTreeViewItem), \
            "Invalid index: {} at ({},{}) {}".format(
                index, index.row(), index.column(), item)
        d = item.declaration
        try:
            c = index.column()  # - d.visible_column
            return d._columns[c].proxy
        except IndexError:
            return


class QtTreeView(QtAbstractItemView, ProxyTreeView):
    #: Tree widget
    widget = Typed(QTreeView)

    #: Root index
    index = Instance(QModelIndex, ())

    def create_widget(self):
        self.widget = QTreeView(self.parent_widget())

    def init_widget(self):
        super(QtTreeView, self).init_widget()
        d = self.declaration
        self.set_show_root(d.show_root)

    def init_model(self):
        self.set_model(QAtomTreeModel(parent=self.widget))

    # -------------------------------------------------------------------------
    # Widget Setters
    # -------------------------------------------------------------------------
    def set_show_root(self, show):
        self.widget.setRootIsDecorated(show)

    def set_cell_padding(self, padding):
        self.widget.setStyleSheet(
            "QTreeView::item { padding: %ipx }" % padding)

    def set_horizontal_minimum_section_size(self, size):
        self.widget.header().setMinimumSectionSize(size)

    def set_horizontal_stretch(self, stretch):
        self.widget.header().setStretchLastSection(stretch)

    def set_horizontal_headers(self, headers):
        self.widget.header().model().layoutChanged.emit()

    def set_resize_mode(self, mode):
        if IS_QT4:
            self.widget.header().setResizeMode(RESIZE_MODES[mode])
        else:
            self.widget.header().setSectionResizeMode(RESIZE_MODES[mode])

    def set_show_horizontal_header(self, show):
        header = self.widget.header()
        header.show() if show else header.hide()

    # -------------------------------------------------------------------------
    # View refresh handlers
    # -------------------------------------------------------------------------
    def _refresh_visible_column(self, value):
        self._pending_column_refreshes -= 1
        if self._pending_column_refreshes == 0:
            d = self.declaration
            # TODO: What about parents???
            try:
                cols = self.model.columnCount(self.index)-d.visible_columns
                d.visible_column = max(0, min(value, cols))
            except RuntimeError:
                #: Since refreshing is deferred several ms later
                pass

    def _refresh_visible_row(self, value):
        self._pending_row_refreshes -= 1
        if self._pending_row_refreshes == 0:
            d = self.declaration
            try:
                rows = self.model.rowCount(self.index)-d.visible_rows
                d.visible_row = max(0, min(value, rows))
            except RuntimeError:
                pass


class AbstractQtTreeViewItem(AbstractQtWidgetItem):
    """ Base TreeViewItem class """

    #: Pending refreshes when loading widgets
    _refresh_count = Int(0)

    #: Time to wait before loading widget
    _loading_interval = Int(100)

    def create_widget(self):
        if self.declaration:
            for child in self.children():
                if isinstance(child, (Pattern, QtWidget)):
                    self.delegate = child

    def set_row(self, row):
        self._update_index()

    def set_column(self, column):
        self._update_index()

    def _default_index(self):
        d = self.declaration
        return self.view.model.index(d.row, d.column, self.parent().index)

    def _update_index(self):
        self.index = self._default_index()
        if self.delegate:
            self._refresh_count +=1
            timed_call(self._loading_interval, self._update_delegate)

    def _update_delegate(self):
        """ Update the delegate cell widget. This is deferred so it
        does not get called until the user is done scrolling.
        """
        self._refresh_count -= 1
        if self._refresh_count != 0:
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
            self.view.widget.setIndexWidget(self.index, delegate.widget)
        except RuntimeError:
            # Since this is deferred, the table could be deleted already
            # and a RuntimeError is possible
            pass

    def _is_visible(self):
        return self.index.isValid()

    def data_changed(self, change):
        """ Notify the model that data has changed in this cell! """
        self.view.model.dataChanged.emit(self.index, self.index)


class QtTreeViewItem(AbstractQtTreeViewItem, ProxyTreeViewItem):

    def _default_view(self):
        """ If this is the root item, return the parent
            which must be a TreeView, otherwise return the
            parent Item's view.
        """
        parent = self.parent()
        if isinstance(parent, QtTreeView):
            return parent
        return parent.view


class QtTreeViewColumn(AbstractQtTreeViewItem, ProxyTreeViewColumn):

    def _default_view(self):
        """ Since the TreeViewColumn must be a child of a TreeViewItem,
            simply return the Item's view.
        """
        return self.parent().view

    def _default_index(self):
        d = self.declaration
        return self.view.model.index(d.row, d.column, self.parent().index)
