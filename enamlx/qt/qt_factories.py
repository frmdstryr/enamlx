# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 23, 2015
"""
from enaml.qt.qt_factories import QT_FACTORIES


def console_factory():
    from .qt_console import QtConsole
    return QtConsole


def double_spin_box_factory():
    from .qt_double_spin_box import QtDoubleSpinBox
    return QtDoubleSpinBox


def key_event_factory():
    from .qt_key_event import QtKeyEvent
    return QtKeyEvent


def occ_viewer_factory():
    from .qt_occ_viewer import QtOccViewer
    return QtOccViewer


def plot_area_factory():
    from .qt_plot_area import QtPlotArea
    return QtPlotArea


def plot_item_2d_factory():
    from .qt_plot_area import QtPlotItem2D
    return QtPlotItem2D


def plot_item_3d_factory():
    from .qt_plot_area import QtPlotItem3D
    return QtPlotItem3D


def plot_item_array_factory():
    from .qt_plot_area import QtPlotItemArray
    return QtPlotItemArray


def plot_item_array_3d_factory():
    from .qt_plot_area import QtPlotItemArray3D
    return QtPlotItemArray3D


def plot_item_list_factory():
    from .qt_plot_area import QtPlotItemList
    return QtPlotItemList


def plot_item_dict_factory():
    from .qt_plot_area import QtPlotItemDict
    return QtPlotItemDict


def table_view_factory():
    from .qt_table_view import QtTableView
    return QtTableView


def table_view_item_factory():
    from .qt_table_view import QtTableViewItem
    return QtTableViewItem


def table_view_row_factory():
    from .qt_table_view import QtTableViewRow
    return QtTableViewRow


def table_view_col_factory():
    from .qt_table_view import QtTableViewColumn
    return QtTableViewColumn

    
def table_widget_factory():
    from .qt_table_widget import QtTableWidget
    return QtTableWidget


def table_widget_item_factory():
    from .qt_table_widget import QtTableWidgetItem
    return QtTableWidgetItem


def table_widget_row_factory():
    from .qt_table_widget import QtTableWidgetRow
    return QtTableWidgetRow


def table_widget_col_factory():
    from .qt_table_widget import QtTableWidgetColumn
    return QtTableWidgetColumn


def tree_view_factory():
    from .qt_tree_view import QtTreeView
    return QtTreeView


def tree_view_item_factory():
    from .qt_tree_view import QtTreeViewItem
    return QtTreeViewItem


def tree_view_col_factory():
    from .qt_tree_view import QtTreeViewColumn
    return QtTreeViewColumn


def tree_widget_factory():
    from .qt_tree_widget import QtTreeWidget
    return QtTreeWidget


def tree_widget_item_factory():
    from .qt_tree_widget import QtTreeWidgetItem
    return QtTreeWidgetItem


def tree_widget_col_factory():
    from .qt_tree_widget import QtTreeWidgetColumn
    return QtTreeWidgetColumn


# Inject the factory 
QT_FACTORIES.update({
    'Console': console_factory,
    'DoubleSpinBox': double_spin_box_factory,
    'KeyEvent': key_event_factory,
    'OccViewer': occ_viewer_factory,
    'PlotArea': plot_area_factory,
    'PlotItem2D': plot_item_2d_factory,
    'PlotItem3D': plot_item_3d_factory,
    'PlotItemArray': plot_item_array_factory,
    'PlotItemArray3D': plot_item_array_3d_factory,
    'PlotItemList': plot_item_list_factory,
    'PlotItemDict': plot_item_dict_factory,
    'TableView': table_view_factory,
    'TableViewItem': table_view_item_factory,
    'TableViewRow': table_view_row_factory,
    'TableViewColumn': table_view_col_factory,
    'TableWidget': table_widget_factory,
    'TableWidgetItem': table_widget_item_factory,
    'TableWidgetRow': table_widget_row_factory,
    'TableWidgetColumn': table_widget_col_factory,
    'TreeView': tree_view_factory,
    'TreeViewItem': tree_view_item_factory,
    'TreeViewColumn': tree_view_col_factory,
    'TreeWidget': tree_widget_factory,
    'TreeWidgetItem': tree_widget_item_factory,
    'TreeWidgetColumn': tree_widget_col_factory,
})

