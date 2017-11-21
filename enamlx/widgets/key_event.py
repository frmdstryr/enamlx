"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 29, 2015
"""
from atom.api import Event, Value, Unicode, Bool, Typed, ForwardTyped, observe
from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl


class ProxyKeyEvent(ProxyControl):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: KeyEvent)

    def set_enabled(self, enabled):
        raise NotImplementedError


class KeyEvent(Control):
    #: Proxy reference
    proxy = Typed(ProxyKeyEvent)

    #: Key text (optional)
    key = d_(Unicode())

    #: Key code (optional)
    key_code = d_(Value())

    #: Listen for events
    enabled = d_(Bool(True))

    #: Fire multiple times when the key is held
    repeats = d_(Bool(True))

    #: Pressed event
    pressed = d_(Event(), writable=False)

    #: Released event
    released = d_(Event(), writable=False)

    @observe('enabled')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.
        """
        super(KeyEvent, self)._update_proxy(change)
