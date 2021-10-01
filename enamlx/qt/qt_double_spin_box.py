# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 29, 2015
"""
from atom.api import Typed
from enamlx.widgets.double_spin_box import ProxyDoubleSpinBox
from enaml.qt.qt_spin_box import QtSpinBox
from qtpy.QtWidgets import QDoubleSpinBox


class QtDoubleSpinBox(QtSpinBox, ProxyDoubleSpinBox):
    """A Qt implementation of an Enaml SpinBox."""

    #: A reference to the widget created by the proxy.
    widget = Typed(QDoubleSpinBox)

    # -------------------------------------------------------------------------
    # Initialization API
    # -------------------------------------------------------------------------
    def create_widget(self):
        """Create the underlying QDoubleSpinBox widget."""
        widget = QDoubleSpinBox(self.parent_widget())
        widget.setKeyboardTracking(False)
        self.widget = widget

    def init_widget(self):
        self.set_decimals(self.declaration.decimals)
        super(QtDoubleSpinBox, self).init_widget()

    # -------------------------------------------------------------------------
    # ProxyDoubleSpinBox API
    # -------------------------------------------------------------------------
    def set_decimals(self, prec):
        self.widget.setDecimals(prec)
