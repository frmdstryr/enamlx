# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
from enaml.qt.qt_factories import QT_FACTORIES
    
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

def tree_widget_factory():
    from .qt_tree_widget import QtTreeWidget
    return QtTreeWidget

def tree_widget_item_factory():
    from .qt_tree_widget import QtTreeWidgetItem
    return QtTreeWidgetItem

def tree_widget_item_col_factory():
    from .qt_tree_widget import QtTreeWidgetItemColumn
    return QtTreeWidgetItemColumn

# Inject the factory 
QT_FACTORIES['TableWidget'] = table_widget_factory
QT_FACTORIES['TableWidgetItem'] = table_widget_item_factory
QT_FACTORIES['TableWidgetRow'] = table_widget_row_factory
QT_FACTORIES['TableWidgetColumn'] = table_widget_col_factory
QT_FACTORIES['TreeWidget'] = tree_widget_factory
QT_FACTORIES['TreeWidgetItem'] = tree_widget_item_factory
QT_FACTORIES['TreeWidgetItemColumn'] = tree_widget_item_col_factory