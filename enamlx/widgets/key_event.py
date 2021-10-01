"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 29, 2015
"""
import sys
from atom.api import Event, List, Bool, Typed, ForwardTyped, observe
from enaml.core.declarative import d_
from enaml.widgets.control import Control, ProxyControl

if sys.version_info.major < 3:
    str = basestring


class ProxyKeyEvent(ProxyControl):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: KeyEvent)

    def set_enabled(self, enabled):
        raise NotImplementedError

    def set_keys(self, keys):
        raise NotImplementedError


class KeyEvent(Control):
    #: Proxy reference
    proxy = Typed(ProxyKeyEvent)

    #: List of keys that or codes to filter
    #: Can be a key letter or code and including modifiers
    #: Ex. Ctrl + r, up, esc, etc..
    #: If empty will fire for any key combination
    keys = d_(List(str))

    #: Listen for events
    enabled = d_(Bool(True))

    #: Fire multiple times when the key is held
    repeats = d_(Bool(True))

    #: Pressed event
    pressed = d_(Event(dict), writable=False)

    #: Released event
    released = d_(Event(dict), writable=False)

    @observe("enabled", "keys")
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        super(KeyEvent, self)._update_proxy(change)
