"""
Created on Sep 26, 2016

@author: jrmarti3
"""
from atom.api import (
    Event,
    List,
    Tuple,
    Bool,
    Int,
    Enum,
    Typed,
    ForwardTyped,
    observe,
    set_default,
)

from enaml.core.declarative import d_

from enaml.widgets.control import Control, ProxyControl


class ProxyOccViewer(ProxyControl):
    """The abstract definition of a proxy SpinBox object."""

    #: A reference to the SpinBox declaration.
    declaration = ForwardTyped(lambda: OccViewer)

    def set_position(self, position):
        raise NotImplementedError

    def set_pan(self, position):
        raise NotImplementedError

    def set_background_gradient(self, gradient):
        raise NotImplementedError

    def set_zoom(self, zoom):
        raise NotImplementedError

    def set_rotation(self, rotation):
        raise NotImplementedError

    def set_selection_mode(self, mode):
        raise NotImplementedError

    def set_selected(self, position):
        raise NotImplementedError

    def set_selected_area(self, area):
        raise NotImplementedError

    def set_double_buffer(self, enabled):
        raise NotImplementedError

    def set_display_mode(self, mode):
        raise NotImplementedError

    def set_trihedron_mode(self, mode):
        raise NotImplementedError

    def set_view_mode(self, mode):
        raise NotImplementedError

    def set_shadows(self, enabled):
        raise NotImplementedError

    def set_reflections(self, enabled):
        raise NotImplementedError

    def set_antialiasing(self, enabled):
        raise NotImplementedError


class OccViewer(Control):
    """A spin box widget which manipulates integer values."""

    #: A reference to the ProxySpinBox object.
    proxy = Typed(ProxyOccViewer)

    #: The minimum value for the spin box. Defaults to 0.
    position = d_(Tuple(Int(strict=False), default=(0, 0)))

    #: Display mode
    display_mode = d_(Enum("shaded", "hlr", "wireframe"))

    #: Selection mode
    selection_mode = d_(Enum("shape", "neutral", "face", "edge", "vertex"))

    #: Selected items
    selection = d_(List(), writable=False)

    #: View direction
    view_mode = d_(Enum("iso", "top", "bottom", "left", "right", "front", "rear"))

    #: Selection event
    # reset_view = d_(Event(),writable=False)

    #: Show tahedron
    trihedron_mode = d_(Enum("right-lower", "disabled"))

    #: Background gradient
    background_gradient = d_(Tuple(Int(), default=(206, 215, 222, 128, 128, 128)))

    #: Use double buffering
    double_buffer = d_(Bool(True))

    #: Display shadows
    shadows = d_(Bool(False))

    #: Display reflections
    reflections = d_(Bool(True))

    #: Enable antialiasing
    antialiasing = d_(Bool(True))

    #: View expands freely in width by default.
    hug_width = set_default("ignore")

    #: View expands freely in height by default.
    hug_height = set_default("ignore")

    #: Events
    #: Raise StopIteration to indicate handling should stop
    on_key_press = d_(Event(), writable=False)
    on_mouse_press = d_(Event(), writable=False)
    on_mouse_release = d_(Event(), writable=False)
    on_mouse_wheel = d_(Event(), writable=False)
    on_mouse_move = d_(Event(), writable=False)

    # --------------------------------------------------------------------------
    # Observers
    # --------------------------------------------------------------------------
    @observe(
        "position",
        "display_mode",
        "view_mode",
        "trihedron_mode",
        "selection_mode",
        "background_gradient",
        "double_buffer",
        "shadows",
        "reflections",
        "antialiasing",
    )
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        # The superclass handler implementation is sufficient.
        super(OccViewer, self)._update_proxy(change)
