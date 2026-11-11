"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
"""

import types
from typing import Optional

import pyqtgraph as pg
from atom.api import Bool, ForwardInstance, Instance, Int, Typed, observe
from enaml.application import timed_call
from enaml.qt.q_resource_helpers import get_cached_qcolor
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_toolkit_object import QtToolkitObject
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget

from enamlx.widgets.plot_area import (
    PlotItem,
    ProxyPlotArea,
    ProxyPlotAxis,
    ProxyPlotItem,
)


def gl_view_widget():
    from pyqtgraph.opengl import GLViewWidget

    return GLViewWidget


class QtPlotArea(QtControl, ProxyPlotArea):
    """PyQtGraph Plot Widget"""

    __weakref__ = None
    widget = Typed(GraphicsLayoutWidget)

    def create_widget(self):
        self.widget = GraphicsLayoutWidget(self.parent_widget())

    def init_layout(self):
        for child in self.children():
            self.child_added(child)

    def child_added(self, child):
        # TODO support layouts
        if isinstance(child, AbstractQtPlotItem):
            d = child.declaration
            kwargs = dict(row=d.row, col=d.column) if d.row or d.column else {}
            self.widget.addItem(child.widget, **kwargs)

    def child_removed(self, child):
        if isinstance(child, AbstractQtPlotItem):
            self.widget.removeItem(child.widget)


class AbstractQtPlotItem(QtToolkitObject, ProxyPlotItem):
    #: So we can receive signals
    __weakref__ = None

    #: Plot item or parent plot item if nested
    widget = Instance(pg.GraphicsWidget)

    #: Actual plot
    plot = Instance(pg.GraphicsObject)

    #: Root or nested graph
    is_root = Bool()

    #: View box
    viewbox = Instance(pg.ViewBox)

    #: The scene
    scene = Instance(pg.GraphicsScene)

    #: Counter to track refreshes
    _pending_refreshes = Int(0)

    def create_widget(self):
        if isinstance(self.parent(), AbstractQtPlotItem):
            self.widget = self.parent_widget()
            self.is_root = False
        else:
            self.is_root = True
            self.widget = pg.PlotItem()

    def init_layout(self):
        super().init_layout()
        self._refresh_axis_items()
        self.refresh_plot()
        self._refresh_limits()

        # Set after plot is generated
        if self.is_root:
            d = self.declaration
            if d.grid:
                self.set_grid(d.grid)
            if d.title:
                self.set_title(d.title)
            if label := d.label_left:
                self.set_label("left", label)
            if label := d.label_right:
                self.set_label("right", label)
            if label := d.label_top:
                self.set_label("top", label)
            if label := d.label_bottom:
                self.set_label("bottom", label)
            if d.show_legend:
                self.set_show_legend(d.show_legend)
            if d.multi_axis:
                self.set_multi_axis(d.multi_axis)
            self.set_antialias(d.antialias)
            self.set_aspect_locked(d.aspect_locked)
            # if d.background:
            #    self.set_background(d.background)

            if f := d.axis_left_ticks:
                self.set_axis_ticks("left", f)
            if f := d.axis_right_ticks:
                self.set_axis_ticks("right", f)
            if f := d.axis_bottom_ticks:
                self.set_axis_ticks("bottom", f)
            if f := d.axis_top_ticks:
                self.set_axis_ticks("top", f)
            self.set_auto_range(d.auto_range)

        self.init_signals()

    def init_signals(self):
        self.widget.sigRangeChanged.connect(self.on_range_changed)
        self.widget.vb.sigResized.connect(self.on_resized)

    def plot_area(self):
        if isinstance(self.parent(), QtPlotArea):
            return self.parent_widget()
        if isinstance(self.parent(), AbstractQtPlotItem):
            return self.parent().parent_widget()
        raise RuntimeError("Unexpected plot widget hierarchy")

    def _format_data(self):
        raise NotImplementedError

    def _format_style(self):
        data = {}
        d = self.declaration
        if d.line_pen:
            data["pen"] = d.line_pen
        if d.shadow_pen:
            data["shadowPen"] = d.shadow_pen
        if d.fill_level:
            data["fillLevel"] = d.fill_level
        if d.fill_brush:
            data["fillBrush"] = d.fill_brush
        if d.step_mode:
            data["stepMode"] = d.step_mode
        # if d.background:
        #    data['background'] = d.background
        if d.symbol:
            data["symbol"] = d.symbol
            if d.symbol_pen:
                data["symbolPen"] = d.symbol_pen
            if d.symbol_brush:
                data["symbolBrush"] = d.symbol_brush
            if d.symbol_size:
                data["symbolSize"] = d.symbol_size

        if d.antialias:
            data["antialias"] = True
        return data

    def _refresh_axis_items(self):
        axis_items = {
            c.declaration.orientation: c.widget
            for c in self.children()
            if isinstance(c, QtPlotAxis)
        }
        self.widget.setAxisItems(axis_items)

    def refresh_plot(self):
        """Defer drawing until all changes are done so we don't draw
        during initialization or when many values change at once.
        """
        self._pending_refreshes += 1
        refresh_time = self.declaration.refresh_time
        timed_call(refresh_time, self._redraw_plot)

    def _redraw_plot(self):
        self._pending_refreshes -= 1
        if self._pending_refreshes > 0:
            return  # Another change occurred

        d = self.declaration
        if d.draw_enabled:
            d.draw(self)
            return

        if plot := self.plot:
            try:
                plot.clear()
            except RuntimeError:
                pass
        if vb := self.viewbox:
            try:
                vb.close()
            except RuntimeError:
                pass

        data = self._format_data()
        style = self._format_style()

        plot_item = self.plot = pg.PlotDataItem(*data, **style)
        if not self.is_root and d.parent.multi_axis:
            self._refresh_multi_axis()
            self.viewbox.addItem(plot_item)
        else:
            self.widget.addItem(plot_item)

    @observe("plot")
    def _refresh_plot_signals(self, change):
        if oldplot := change.get("oldvalue", None):
            if scene := oldplot.scene():
                scene.sigMouseClicked.disconnect(self.on_mouse_clicked)
                scene.sigMouseMoved.disconnect(self.on_mouse_moved)
        if plot := change.get("value", None):
            if scene := plot.scene():
                d = self.declaration
                scene.sigMouseClicked.connect(self.on_mouse_clicked)
                scene.sigMouseMoved.connect(self.on_mouse_moved)

    def _refresh_multi_axis(self):
        """If linked axis' are used, setup and link them"""
        d = self.declaration

        #: Create a separate viewbox
        self.viewbox = pg.ViewBox()

        #: If this is the first nested plot, use the parent right axis
        _plots = [
            c for c in self.parent().children() if isinstance(c, AbstractQtPlotItem)
        ]
        i = _plots.index(self)
        if i == 0:
            axis = self.widget.getAxis("right")
            self.widget.showAxis("right")
        else:
            axis = self.widget.getAxis("right")
            axis.setZValue(-10000)

            #: Add new axis to scene
            self.widget.layout.addItem(axis, 2, i + 2)

        #: Link x axis to the parent axis
        self.viewbox.setXLink(self.widget.vb)
        self.viewbox.setYLink(self.widget.vb)

        #: Link y axis to the view
        axis.linkToView(self.viewbox)

        #: Set axis label
        # axis.setLabel(d.label_right)

        #: Add Viewbox to parent scene
        self.plot_area().scene().addItem(self.viewbox)
        self.on_resized()

    def _refresh_limits(self):
        d = self.declaration
        limits = {}
        if d.pan_x_min is not None:
            limits["xMin"] = d.pan_x_min
        if d.pan_x_max is not None:
            limits["xMax"] = d.pan_x_max
        if d.pan_y_min is not None:
            limits["yMin"] = d.pan_y_min
        if d.pan_y_max is not None:
            limits["yMax"] = d.pan_y_max
        self.widget.vb.setLimits(**limits)

    def index_at_point(self, point) -> Optional[int]:
        vb = self.viewbox or self.widget.vb
        try:
            return int(vb.mapSceneToView(point).x())
        except Exception:
            return None

    def set_row(self, row):
        self.refresh_plot()

    def set_column(self, column):
        self.refresh_plot()

    def set_aspect_locked(self, locked):
        self.widget.setAspectLocked(locked)

    def set_background(self, background):
        color = get_cached_qcolor(background) if background else None
        area = self.plot_area()
        area.setBackground(color)

    def set_line_pen(self, pen):
        self.widget.setPen(pen)

    def set_shadow_pen(self, pen):
        self.widget.setShadowPen(pen)

    def set_axis_items(self, axis_items: Optional[dict[str, "pg.AxisItem"]]):
        self.widget.setAxisItems(axis_items)

    def set_axis_left_ticks(self, callback):
        self.set_axis_ticks("left", callback)

    def set_axis_bottom_ticks(self, callback):
        self.set_axis_ticks("bottom", callback)

    def set_axis_ticks(self, axis_name, callback):
        axis = self.widget.getAxis(axis_name)

        # Save ref
        if not hasattr(axis, "_tickStrings"):
            axis._tickStrings = axis.tickStrings
        axis.tickStrings = (
            types.MethodType(callback, axis, axis.__class__)
            if callback
            else axis._tickStrings
        )

    def set_grid(self, grid: tuple[bool, bool], alpha: Optional[float] = None):
        a = alpha or self.declaration.grid_alpha
        self.widget.showGrid(grid[0], grid[1], a)

    def set_grid_alpha(self, alpha):
        self.set_grid(self.declaration.grid)

    def set_show_legend(self, show: bool):
        if show:
            if not self.widget.legend:
                self.widget.addLegend()
        else:
            self.widget.legend.hide()

    def set_title(self, title):
        self.widget.setTitle(title)

    def set_label(self, axis: str, text: str):
        self.widget.setLabel(axis, text)

    def set_label_top(self, text):
        self.set_label("top", text)

    def set_label_left(self, text):
        self.set_label("left", text)

    def set_label_right(self, text):
        if not self.is_root and self.declaration.parent.multi_axis:
            return  # don't override multi axis label
        self.set_label("right", text)

    def set_label_bottom(self, text):
        self.set_label("bottom", text)

    def set_auto_downsampling(self, enabled):
        self.widget.setDownsampling(auto=enabled)

    def set_antialias(self, enabled):
        self.refresh_plot()

    def set_pan_x_min(self, limit: Optional[float]):
        self._refresh_limits()

    def set_pan_x_max(self, limit: Optional[float]):
        self._refresh_limits()

    def set_pan_y_min(self, limit: Optional[float]):
        self._refresh_limits()

    def set_pan_y_max(self, limit: Optional[float]):
        self._refresh_limits()

    def set_auto_range(self, auto_range):
        d = self.declaration
        if not isinstance(auto_range, tuple):
            auto_range = (auto_range, auto_range)
            self.declaration.auto_range = auto_range
        if not auto_range[0]:
            self.set_range_x(d.range_x)
        if not auto_range[1]:
            self.set_range_y(d.range_y)

    #
    # Setters that require a full refresh
    #
    def set_draw_enabled(self, arg):
        self._redraw_plot()

    def set_symbol(self, arg):
        self.refresh_plot()

    def set_symbol_size(self, arg):
        self.refresh_plot()

    def set_symbol_brush(self, arg):
        self.refresh_plot()

    def set_fill_brush(self, arg):
        self.refresh_plot()

    def set_fill_level(self, arg):
        self.refresh_plot()

    def set_multi_axis(self, arg):
        self.refresh_plot()

    def set_log_mode(self, arg):
        self.refresh_plot()

    def set_clip_to_view(self, arg):
        self.refresh_plot()

    def set_step_mode(self, arg):
        self.refresh_plot()

    def set_range_x(self, val):
        """Set visible range of x data.

        Note: Padding must be 0 or it will create an infinite loop

        """
        d = self.declaration
        if d.auto_range[0]:
            return
        self.widget.setXRange(*val, padding=0)

    def set_range_y(self, val):
        """Set visible range of y data.

        Note: Padding must be 0 or it will create an infinite loop

        """
        d = self.declaration
        if d.auto_range[1]:
            return
        self.widget.setYRange(*val, padding=0)

    # -------------------------------------------------------------------------
    # Widget events
    # -------------------------------------------------------------------------
    def on_range_changed(self, vb, rect: tuple[list[int], list[int]]):
        d = self.declaration
        d.range_x = rect[0]
        d.range_y = rect[1]

    def on_scale_changed(self, view_scale):
        pass

    def on_resized(self):
        """Update linked views"""
        d = self.declaration
        if not self.is_root and d.parent.multi_axis:
            if vb := self.viewbox:
                vb.setGeometry(self.widget.vb.sceneBoundingRect())
                vb.linkedViewChanged(self.widget.vb, vb.XAxis)

    def on_mouse_clicked(self, e):
        self.declaration.clicked(e)

    def on_mouse_moved(self, e):
        self.declaration.mouse_moved(e)

    # -------------------------------------------------------------------------
    # Child events
    # -------------------------------------------------------------------------
    def child_added(self, child):
        if isinstance(child, QtPlotAxis):
            self._refresh_axis_items()
        elif isinstance(child, AbstractQtPlotItem):
            self._redraw_plot()

    def child_removed(self, child):
        if isinstance(child, QtPlotAxis):
            self._refresh_axis_items()
        elif isinstance(child, AbstractQtPlotItem):
            self._redraw_plot()


class QtPlotAxis(QtToolkitObject, ProxyPlotAxis):
    widget = Instance(pg.AxisItem)

    def create_widget(self):
        d = self.declaration
        kwargs = {
            "orientation": d.orientation,
            "showValues": d.show_values,
            "parent": self.parent_widget(),
        }
        if d.mode == "date":
            self.widget = pg.DateAxisItem(**kwargs)
        else:
            self.widget = pg.AxisItem(**kwargs)

    def init_widget(self):
        axis = self.widget
        d = self.declaration
        if d.pen:
            axis.setPen(d.pen)
        if label := d.label:
            axis.setLabel(label, units=d.units, unitPrefix=d.unit_prefix)


class QtPlotItem2D(AbstractQtPlotItem):
    def set_x(self, x):
        # Only refresh when they are equal
        # because one can be set at a time
        if len(self.declaration.y) == len(x):
            self.refresh_plot()

    def set_y(self, y):
        # Only refresh when they are equal
        # because one can be set at a time
        if len(self.declaration.x) == len(y):
            self.refresh_plot()

    def _format_data(self):
        data = [self.declaration.y]
        if self.declaration.x is not None:
            data.insert(0, self.declaration.x)
        return data


class QtPlotItemDict(QtPlotItem2D):
    def set_data(self, data):
        self.refresh_plot()

    def _format_data(self):
        data = self.declaration.data
        return (data,)


class QtPlotItemList(QtPlotItemDict):
    pass


class QtPlotItemArray(QtPlotItem2D):
    pass


class QtPlotItem3D(QtPlotItem2D):
    """Use forward instance to not cause import issues if
    not installed."""

    widget = ForwardInstance(gl_view_widget)

    def create_widget(self):
        from pyqtgraph.opengl import GLViewWidget

        if isinstance(self.parent(), AbstractQtPlotItem):
            self.widget = self.parent_widget()
        else:
            self.widget = GLViewWidget(parent=self.parent_widget())
            self.widget.opts["distance"] = 40
            self.widget.raise_()

    def init_signals(self):
        pass

    def _create_grid(self):
        from pyqtgraph.opengl import GLGridItem

        gx = GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.widget.addItem(gx)
        gy = GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.widget.addItem(gy)
        gz = GLGridItem()
        gz.translate(0, 0, -10)
        self.widget.addItem(gz)

    def set_z(self, z):
        self.refresh_plot()

    def _refresh_plot(self):
        import numpy as np

        # import pyqtgraph as pg
        from pyqtgraph import opengl as gl

        self._create_grid()
        pts = np.vstack(
            [self.declaration.x, self.declaration.y, self.declaration.z]
        ).transpose()
        plt = gl.GLLinePlotItem(
            pos=pts
        )  # , color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
        self.widget.addItem(plt)

    def set_grid(self, grid):
        pass


class QtPlotItemArray3D(QtPlotItem3D):
    def _refresh_plot(self):
        import numpy as np
        import pyqtgraph as pg
        from pyqtgraph import opengl as gl

        self._create_grid()
        n = 51
        x = self.declaration.x
        y = self.declaration.y
        for i in range(n):
            yi = np.array([y[i]] * 100)
            d = (x**2 + yi**2) ** 0.5
            z = 10 * np.cos(d) / (d + 1)
            pts = np.vstack([x, yi, z]).transpose()
            plt = gl.GLLinePlotItem(
                pos=pts,
                color=pg.glColor((i, n * 1.3)),
                width=(i + 1) / 10.0,
                antialias=True,
            )
        self.widget.addItem(plt)


#     def set_data(self,data):
#         self.widget.plotItem.clear()
#         if self._views:
#             for view in self._views:
#                 view.clear()
#
#         views = []
#         i = 0
#         if self.declaration.multi_axis:
#             for i,plot in enumerate(data):
#                 if i>3:
#                     break
#                 if 'pen' not in plot:
#                     plot['pen'] = self._colors[i]
#                 if i>0:
#                     view = ViewBox()
#                     views.append(view)
#                     self.widget.plotItem.scene().addItem(view)
#                     if i==1:
#                         axis = self.widget.plotItem.getAxis('right')
#                     elif i>1:
#                         axis = AxisItem('right')
#                         axis.setZValue(-10000)
#                         self.widget.plotItem.layout.addItem(axis,2,3)
#                     axis.linkToView(view)
#                     view.setXLink(self.widget.plotItem)
#                     view.addItem(PlotCurveItem(**plot))
#                 else:    #view.setYLink(self.widget.plotItem)
#                     self.widget.plot(**plot)
#         if i>0:
#             def syncViews():
#                 for v in views:
#                     v.setGeometry(self.widget.plotItem.vb.sceneBoundingRect())
#                     v.linkedViewChanged(self.widget.plotItem.vb,v.XAxis)
#             syncViews()
#             self.widget.plotItem.vb.sigResized.connect(syncViews)
#         self._views = views
