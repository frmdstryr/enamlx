# -*- coding: utf-8 -*-
'''
Created on Aug 29, 2015

@author: jrm
'''
from atom.api import Typed
from enamlx.widgets.double_spin_box import ProxyDoubleSpinBox
from enaml.qt.qt_spin_box import QtSpinBox
from enaml.qt.QtGui import QDoubleSpinBox

class QtDoubleSpinBox(QtSpinBox, ProxyDoubleSpinBox):
    """ A Qt implementation of an Enaml SpinBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDoubleSpinBox)
    
    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDoubleSpinBox widget.

        """
        widget = QDoubleSpinBox(self.parent_widget())
        widget.setKeyboardTracking(False)
        self.widget = widget