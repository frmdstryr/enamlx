# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Jun 11, 2015
"""
import sys
from atom.atom import set_default
from atom.api import (
    Callable,
    Int,
    Tuple,
    Instance,
    Enum,
    Float,
    ContainerList,
    Bool,
    FloatRange,
    Str,
    Dict,
    Typed,
    ForwardTyped,
    observe,
)
from enaml.core.declarative import d_
from enaml.widgets.api import Container
from enaml.widgets.control import Control, ProxyControl
from atom.instance import ForwardInstance

if sys.version_info.major < 3:
    str = basestring


def numpy_ndarray():
    import numpy

    return numpy.ndarray


class ProxyPlotArea(ProxyControl):
    declaration = ForwardTyped(lambda: PlotArea)


class PlotArea(Container):
    hug_width = set_default("ignore")
    hug_height = set_default("ignore")
    proxy = Typed(ProxyPlotArea)
    setup = d_(Callable(lambda graph: None))


PEN_ARGTYPES = (tuple, list, str, dict)
BRUSH_ARGTYPES = (tuple, list, str, dict, int, float)


class PlotItem(Control):
    #: Title of data series
    title = d_(Str())

    #: Name
    name = d_(Str())

    #: Row in plot area
    row = d_(Int(0))

    #: Column in plot area
    column = d_(Int(0))

    #: Pen type to use for line
    line_pen = d_(Instance(PEN_ARGTYPES))

    #: Pen type to use for shadow
    shadow_pen = d_(Instance(PEN_ARGTYPES))

    #: Fill level
    fill_level = d_(Float(strict=False))

    # ‘c’     one of: r, g, b, c, m, y, k, w
    # R, G, B, [A]     integers 0-255
    # (R, G, B, [A])     tuple of integers 0-255
    # float     greyscale, 0.0-1.0
    # int     see intColor()
    # (int, hues)     see intColor()
    # “RGB”     hexadecimal strings; may begin with ‘#’
    # “RGBA”
    # “RRGGBB”
    # “RRGGBBAA”
    #: Brush fill type
    fill_brush = d_(Instance(BRUSH_ARGTYPES))

    #: Symbol to use for points
    symbol = d_(Enum(None, "o", "s", "t", "d", "+"))

    #: Symbol sizes for points
    symbol_size = d_(Float(10, strict=False))

    #: Symbol pen to use
    symbol_pen = d_(Instance(PEN_ARGTYPES))

    #: Symbol brush
    symbol_brush = d_(Instance(BRUSH_ARGTYPES))

    #: Show legend
    show_legend = d_(Bool(False))

    label_left = d_(Str())
    label_right = d_(Str())
    label_top = d_(Str())
    label_bottom = d_(Str())

    # H, V
    grid = d_(Tuple(bool, default=(False, False)))
    grid_alpha = d_(FloatRange(low=0.0, high=1.0, value=0.5))

    #: Display a separate axis for each nested plot
    multi_axis = d_(Bool(True))

    axis_left_ticks = d_(Callable())
    axis_bottom_ticks = d_(Callable())

    #: Display the axis on log scale
    log_mode = d_(Tuple(bool, default=(False, False)))  # x,y

    #: Enable antialiasing
    antialias = d_(Bool(False))

    #: Set auto range for each axis
    auto_range = d_(
        Enum(True, False, (True, True), (True, False), (False, True), (False, False))
    )

    # x-range to use if auto_range is disabled
    range_x = d_(ContainerList(default=[0, 100]))

    #: y-range to use if auto_range is disabled
    range_y = d_(ContainerList(default=[0, 100]))

    #: Automatically downsaple
    auto_downsample = d_(Bool(False))

    #: Clip data points to view
    clip_to_view = d_(Bool(False))

    #: Step mode to use
    step_mode = d_(Bool(False))

    #: Keep aspect ratio locked when resizing
    aspect_locked = d_(Bool(False))

    #: Time between updates
    refresh_time = d_(Int(100))

    @observe(
        "line_pen",
        "symbol",
        "symbol_size",
        "symbol_pen",
        "symbol_brush",
        "fill_brush",
        "fill_level",
        "multi_axis",
        "title",
        "label_left",
        "label_right",
        "label_top",
        "label_bottom",
        "grid",
        "grid_alpha",
        "log_mode",
        "antialias",
        "auto_range",
        "auto_downsample",
        "clip_to_view",
        "step_mode",
        "aspect_locked",
        "axis_left_ticks",
        "axis_bottom_ticks",
        "show_legend",
        "row",
        "column",
    )
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        # The superclass handler implementation is sufficient.
        super(PlotItem, self)._update_proxy(change)

    @observe("range_x", "range_y")
    def _update_range(self, change):
        """Handle updates and changes"""
        getattr(self.proxy, "set_%s" % change["name"])(change["value"])


class PlotItem2D(PlotItem):

    #: x-axis values, as a list
    x = d_(ContainerList())

    #: y-axis values, as a list
    y = d_(ContainerList())

    @observe("x", "y")
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        # The superclass handler implementation is sufficient.
        super(PlotItem2D, self)._update_proxy(change)


class PlotItem3D(PlotItem2D):

    #: z-axis values, as a list
    z = d_(ContainerList())

    @observe("z")
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        # The superclass handler implementation is sufficient.
        super(PlotItem3D, self)._update_proxy(change)


class PlotItemArray(PlotItem2D):
    """Numpy array item"""

    #: x-axis values, as a numpy array
    x = d_(ForwardInstance(numpy_ndarray))

    #: y-axis values, as a numpy array
    y = d_(ForwardInstance(numpy_ndarray))


class PlotItemArray3D(PlotItem3D):
    """Numpy array item"""

    #: Plot type
    type = Enum("line")

    #: x-axis values, as a numpy array
    x = d_(ForwardInstance(numpy_ndarray))

    #: y-axis values, as a numpy array
    y = d_(ForwardInstance(numpy_ndarray))

    #: z-axis values, as a numpy array
    z = d_(ForwardInstance(numpy_ndarray))


class AbstractDataPlotItem(PlotItem):
    @observe("data")
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        # The superclass handler implementation is sufficient.
        super(AbstractDataPlotItem, self)._update_proxy(change)


class PlotItemList(AbstractDataPlotItem):
    data = d_(ContainerList())


class PlotItemDict(AbstractDataPlotItem):
    data = d_(Dict(default={"x": [], "y": []}))
