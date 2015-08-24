# -*- coding: utf-8 -*-
'''
Created on Aug 23, 2015

@author: jrm
'''
    
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

# Inject the factory 
from enaml.qt.qt_factories import QT_FACTORIES
QT_FACTORIES['TableWidget'] = table_widget_factory
QT_FACTORIES['TableWidgetItem'] = table_widget_item_factory
QT_FACTORIES['TableWidgetRow'] = table_widget_row_factory
QT_FACTORIES['TableWidgetColumn'] = table_widget_col_factory