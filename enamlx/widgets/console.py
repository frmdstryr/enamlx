# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Oct 2, 2016
"""

from atom.api import (
    Instance, Coerced, Int, Enum, Unicode, Dict, Bool,
    Typed, ForwardTyped, observe
)
from enaml.core.api import d_
from enaml.widgets.control import ProxyControl
from enaml.widgets.container import Container
from enaml.layout.geometry import Size

class ProxyConsole(ProxyControl):
    declaration = ForwardTyped(lambda: Console)
    
    def set_console_size(self,size):
        raise NotImplementedError
    
    def set_font_size(self, size):
        raise NotImplementedError
    
    def set_font_family(self, family):
        raise NotImplementedError
    
    def set_buffer_size(self, size):
        raise NotImplementedError
    
    def set_display_banner(self,enabled):
        raise NotImplementedError
    
    def set_completion(self, mode):
        raise NotImplementedError
        
    def set_scope(self,scope):
        raise NotImplementedError
    
    def set_execute(self,cmds):
        raise NotImplementedError

class Console(Container):
    """ Console widget """
    proxy = Typed(ProxyConsole)
    
    #: Font family, leave blank for default
    font_family = d_(Unicode())
    
    #: Font size, leave 0 for default
    font_size = d_(Int(0))
    
    #: Default console size in characters
    console_size = d_(Coerced(Size,(81,25)))
    
    #: Buffer size, leave 0 for default
    buffer_size = d_(Int(0))
    
    #: Display banner like version, etc..
    display_banner = d_(Bool(False))
    
    #: Code completion type
    #: Only can be set ONCE
    completion = d_(Enum('ncurses','plain', 'droplist'))
    
    #: Run the line or callabla
    execute = d_(Instance(object))
    
    #: Push variables to the console
    #: Note this is WRITE ONLY
    scope = d_(Dict(),readable=False)
    
    @observe('font_family','font_size','console_size','buffer_size',
             'scope','display_banner','execute','completion')
    def _update_proxy(self, change):
        super(Console, self)._update_proxy(change)
    
 