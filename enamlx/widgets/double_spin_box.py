# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 29, 2015
"""
from atom.api import (Float, ForwardTyped)
from enaml.core.declarative import d_
from enaml.widgets.spin_box import SpinBox, ProxySpinBox


class ProxyDoubleSpinBox(ProxySpinBox):
    declaration = ForwardTyped(lambda: DoubleSpinBox)


class DoubleSpinBox(SpinBox):
    """ A spin box widget which manipulates float values.

    """
    #: The minimum value for the spin box. Defaults to 0.
    minimum = d_(Float(0, strict=False))

    #: The maximum value for the spin box. Defaults to 100.
    maximum = d_(Float(100, strict=False))
    
    #: The maximum value for the spin box. Defaults to 100.
    single_step = d_(Float(1.0, strict=False))

    #: The position value of the spin box. The value will be clipped to
    #: always fall between the minimum and maximum.
    value = d_(Float(0, strict=False))