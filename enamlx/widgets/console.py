# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2016

@author: jrm
'''

from atom.api import (Enum, Typed, ForwardTyped)
from enaml.core.api import d_
from enaml.widgets.control import ProxyControl
from enaml.widgets.container import Container

class ProxyConsole(ProxyControl):
    declaration = ForwardTyped(lambda: Console)

class Console(Container):
    """ Console widget which manipulates float values.

    """
    proxy = Typed(ProxyConsole)
    
    gui = d_(Enum('qt4','qt5'))