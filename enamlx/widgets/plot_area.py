# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Jun 11, 2015
"""
import sys

from atom.api import (
    Bool,
    Callable,
    ContainerList,
    Dict,
    Enum,
    Event,
    FixedTuple,
    Float,
    FloatRange,
    ForwardInstance,
    ForwardTyped,
    Instance,
    Int,
    Str,
    Tuple,
    Typed,
    Value,
    observe,
)
from atom.atom import set_default
from enaml.core.declarative import d_, d_func
from enaml.widgets.api import Container
from enaml.widgets.control import Control, ProxyControl
from enaml.widgets.toolkit_object import ProxyToolkitObject, ToolkitObject
from typing import Optional

if sys.version_info.major < 3:
    str = basestring  # noqa: F821


def numpy_ndarray():
    import numpy

    return numpy.ndarray


class ProxyPlotArea(ProxyControl):
    declaration = ForwardTyped(lambda: PlotArea)


class PlotArea(Control):
    proxy = Typed(ProxyPlotArea)

    hug_width = set_default("ignore")
    hug_height = set_default("ignore")

    setup = d_(Callable(lambda graph: None))


PEN_ARGTYPES = (tuple, list, str, dict)
BRUSH_ARGTYPES = (tuple, list, str, dict, int, float)


class ProxyPlotItem(ProxyToolkitObject):
    declaration = ForwardInstance(lambda: PlotItem)

    def refresh_plot(self):
        raise NotImplementedError()

    def index_at_point(self, point) -> Optional[int]:
        raise NotImplementedError()


class PlotItem(ToolkitObject):
    #: The dec
    proxy = Instance(ProxyPlotItem)

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

    #: Axis label shortcuts
    label_left = d_(Str())
    label_right = d_(Str())
    label_top = d_(Str())
    label_bottom = d_(Str())

    # H, V
    grid = d_(FixedTuple(bool, bool, default=(False, False)))
    grid_alpha = d_(FloatRange(low=0.0, high=1.0, value=0.5))

    #: Display a separate axis for each nested plot
    multi_axis = d_(Bool(True))

    axis_left_ticks = d_(Callable())
    axis_right_ticks = d_(Callable())
    axis_bottom_ticks = d_(Callable())
    axis_top_ticks = d_(Callable())

    #: Display the axis on log scale
    log_mode = d_(Tuple(bool, default=(False, False)))  # x,y

    #: Enable antialiasing
    antialias = d_(Bool(False))

    #: Set auto range for each axis
    auto_range = d_(FixedTuple(bool, bool, default=(True, True)))

    # Panning limits
    pan_x_min = d_(Typed(float))
    pan_x_max = d_(Typed(float))
    pan_y_min = d_(Typed(float))
    pan_y_max = d_(Typed(float))

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

    #: Call custom draw function
    draw_enabled = d_(Bool(False))

    #: Triggered when the plot is clicked.
    #: The event value contains the pyqtgraph MouseClickEvent
    clicked = d_(Event())

    #: Triggered when mouse is moved over the plot
    #: The event value contains the qt click point
    mouse_moved = d_(Event())

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
        "axis_right_ticks",
        "axis_top_ticks",
        "axis_bottom_ticks",
        "pan_x_min",
        "pan_x_max",
        "pan_y_min",
        "pan_y_max",
        "show_legend",
        "row",
        "column",
        "draw_enabled",
    )
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        # The superclass handler implementation is sufficient.
        super(PlotItem, self)._update_proxy(change)

    @observe("range_x")
    def _update_range_x(self, change):
        self.proxy.set_range_x(change["value"])

    @observe("range_y")
    def _update_range_y(self, change):
        self.proxy.set_range_y(change["value"])

    @d_func
    def draw(self, widget):
        """A method invoked to manually draw the plot.
        This is only invoked when `draw_enabled = True`

        Parameters
        ----------
        widget: Widget
            The underlying proxy widget.
        """
        raise NotImplementedError()

    def index_at_point(self, point) -> Optional[int]:
        """ Get the index in data from the given point """
        return self.proxy.index_at_point(point)


class ProxyPlotAxis(ProxyToolkitObject):
    declaration = ForwardTyped(lambda: PlotAxis)


class PlotAxis(ToolkitObject):
    proxy = Typed(ProxyPlotAxis)

    #: Label to display
    label = d_(Str())

    #: Label units
    units = d_(Typed(str))

    #: Label unit prefix
    unit_prefix = d_(Typed(str))

    #: Axis range of type tuple[float, float]
    display_range = d_(Typed(tuple))

    #: Pen type to use for the axis
    pen = d_(Instance(PEN_ARGTYPES))

    #: Pen type to use for the axis text
    text_pen = d_(Instance(PEN_ARGTYPES))

    #: Pen type to use for the axis ticks
    tick_pen = d_(Instance(PEN_ARGTYPES))

    #: Whether to display values adjacent to ticks
    show_values = d_(Bool(True))

    #: Whether to show the label
    show_label = d_(Bool(True))

    #: Whether axis values should be displayed as dates
    mode = d_(Enum("numeric", "date"))

    #: Side of the plot the axis is attached to
    orientation = d_(Enum("left", "right", "top", "bottom"))

    #: Range of values to link to
    link_to = d_(Instance(PlotItem))

    #: Callable to generate custom ticks
    ticks = d_(Callable())

    @observe("label", "units","unit_prefix",  "pen", "text_pen", "tick_pen")
    def _update_proxy(self, change):
        """An observer which sends state change to the proxy."""
        self.proxy.init_widget()


class PlotItem2D(PlotItem):
    #: x-axis values, as a list
    x = d_(ContainerList())

    #: y-axis values, as a list
    y = d_(ContainerList())

    @observe("x", "y")
    def _update_proxy(self, change):
        self.proxy.refresh_plot()


class PlotItem3D(PlotItem2D):
    #: z-axis values, as a list
    z = d_(ContainerList())

    @observe("z")
    def _update_proxy(self, change):
        self.proxy.refresh_plot()


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
    data = d_(Value())

    @observe("data")
    def _update_proxy(self, change):
        self.proxy.refresh_plot()


class PlotItemList(AbstractDataPlotItem):
    data = d_(ContainerList())


class PlotItemDict(AbstractDataPlotItem):
    data = d_(Dict(default={"x": [], "y": []}))
