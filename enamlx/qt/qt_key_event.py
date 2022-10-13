# -*- coding: utf-8 -*-
"""
Copyright (c) 2015-2022, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 29, 2015
"""
from atom.api import Callable, Dict, Instance
from enaml.qt.qt_control import QtControl
from qtpy import QtCore

from enamlx.widgets.key_event import ProxyKeyEvent

Qt = QtCore.Qt
MODIFIERS = {
    "": Qt.NoModifier,
    "shift": Qt.ShiftModifier,
    "ctrl": Qt.ControlModifier,
    "alt": Qt.AltModifier,
    "meta": Qt.MetaModifier,
    "keypad": Qt.KeypadModifier,
    "group": Qt.GroupSwitchModifier,
}

KEYS = {
    k.split("Key_")[-1].lower(): getattr(Qt, k)
    for k in Qt.__dict__
    if k.startswith("Key_")
}


class QtKeyEvent(QtControl, ProxyKeyEvent):

    # Reference to the original handler
    _keyPressEvent = Callable()

    # Reference to the original handler
    _keyReleaseEvent = Callable()

    #: Widget that this key press handler is overriding
    widget = Instance(QtCore.QObject)

    #: Key codes to match
    codes = Dict()

    def create_widget(self):
        """The KeyEvent uses the parent_widget as it's widget"""
        self.widget = self.parent_widget()

    def init_widget(self):
        """The KeyEvent uses the parent_widget as it's widget"""
        super(QtKeyEvent, self).init_widget()
        d = self.declaration
        widget = self.widget
        self._keyPressEvent = widget.keyPressEvent
        self._keyReleaseEvent = widget.keyReleaseEvent
        self.set_enabled(d.enabled)
        self.set_keys(d.keys)

    # -------------------------------------------------------------------------
    # ProxyKeyEvent API
    # -------------------------------------------------------------------------
    def set_enabled(self, enabled):
        widget = self.widget
        if enabled:
            widget.keyPressEvent = lambda event: self.on_key_press(event)
            widget.keyReleaseEvent = lambda event: self.on_key_release(event)
        else:
            # Restore original
            widget.keyPressEvent = self._keyPressEvent
            widget.keyReleaseEvent = self._keyReleaseEvent

    def set_keys(self, keys):
        """Parse all the key codes and save them"""
        codes = {}
        for key in keys:
            parts = [k.strip().lower() for k in key.split("+")]
            code = KEYS.get(parts[-1])
            modifier = Qt.KeyboardModifier(0)
            if code is None:
                raise KeyError("Invalid key code '{}'".format(key))
            if len(parts) > 1:
                for mod in parts[:-1]:
                    mod_code = MODIFIERS.get(mod)
                    if mod_code is None:
                        raise KeyError("Invalid key modifier '{}'".format(mod_code))
                    modifier |= mod_code
            if code not in codes:
                codes[code] = []
            codes[code].append(modifier)
        self.codes = codes

    # -------------------------------------------------------------------------
    # QWidget Keys API
    # -------------------------------------------------------------------------
    def is_matching_key(self, code, mods):
        codes = self.codes.get(code, None)
        if codes is None:
            return False
        return mods in codes

    def on_key_press(self, event):
        d = self.declaration
        try:
            code = event.key()
            mods = event.modifiers()
            is_repeat = event.isAutoRepeat()
            if not self.codes or self.is_matching_key(code, mods):
                if not d.repeats and is_repeat:
                    return
                d.pressed(
                    {
                        "code": code,
                        "modifiers": mods,
                        "key": event.text(),
                        "repeated": is_repeat,
                    }
                )

        finally:
            self._keyPressEvent(event)

    def on_key_release(self, event):
        d = self.declaration
        try:
            code = event.key()
            mods = event.modifiers()
            is_repeat = event.isAutoRepeat()
            if not self.codes or self.is_matching_key(code, mods):
                if not d.repeats and is_repeat:
                    return
                d.released(
                    {
                        "code": code,
                        "key": event.text(),
                        "modifiers": mods,
                        "repeated": is_repeat,
                    }
                )
        finally:
            self._keyReleaseEvent(event)
