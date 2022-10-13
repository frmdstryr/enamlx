# -*- coding: utf-8 -*-
"""
Copyright (c) 2018, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Sept 4, 2018
"""
import warnings

from atom.api import Atom, Coerced, Int, Typed, atomref
from enaml.drag_drop import DropAction
from enaml.qt.q_resource_helpers import (
    get_cached_qcolor,
    get_cached_qfont,
    get_cached_qimage,
)
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_drag_drop import QtDropEvent
from enaml.qt.qt_toolkit_object import QtToolkitObject
from enaml.qt.qt_widget import QtWidget, focus_registry
from enaml.qt.QtCore import QPoint, QPointF, QRectF, Qt
from enaml.qt.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QDrag,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
)
from enaml.qt.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsLineItem,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QWidgetAction,
)
from enaml.widgets.widget import Feature

from enamlx.widgets.graphics_view import (
    GraphicFeature,
    Point,
    ProxyAbstractGraphicsShapeItem,
    ProxyGraphicsEllipseItem,
    ProxyGraphicsImageItem,
    ProxyGraphicsItem,
    ProxyGraphicsItemGroup,
    ProxyGraphicsLineItem,
    ProxyGraphicsPathItem,
    ProxyGraphicsPolygonItem,
    ProxyGraphicsRectItem,
    ProxyGraphicsTextItem,
    ProxyGraphicsView,
    ProxyGraphicsWidget,
)

PEN_STYLES = {
    "none": Qt.NoPen,
    "solid": Qt.SolidLine,
    "dash": Qt.DashLine,
    "dot": Qt.DotLine,
    "dash_dot": Qt.DashDotLine,
    "dash_dot_dot": Qt.DashDotDotLine,
    "custom": Qt.CustomDashLine,
}

CAP_STYLES = {
    "square": Qt.SquareCap,
    "flat": Qt.FlatCap,
    "round": Qt.RoundCap,
}

JOIN_STYLES = {
    "bevel": Qt.BevelJoin,
    "miter": Qt.MiterJoin,
    "round": Qt.RoundJoin,
}

BRUSH_STYLES = {
    "solid": Qt.SolidPattern,
    "dense1": Qt.Dense1Pattern,
    "dense2": Qt.Dense2Pattern,
    "dense3": Qt.Dense3Pattern,
    "dense4": Qt.Dense4Pattern,
    "dense5": Qt.Dense5Pattern,
    "dense6": Qt.Dense6Pattern,
    "dense7": Qt.Dense7Pattern,
    "horizontal": Qt.HorPattern,
    "vertical": Qt.VerPattern,
    "cross": Qt.CrossPattern,
    "bdiag": Qt.BDiagPattern,
    "fdiag": Qt.FDiagPattern,
    "diag": Qt.DiagCrossPattern,
    "linear": Qt.LinearGradientPattern,
    "radial": Qt.RadialGradientPattern,
    "conical": Qt.ConicalGradientPattern,
    "texture": Qt.TexturePattern,
    "none": Qt.NoBrush,
}


DRAG_MODES = {
    "none": QGraphicsView.NoDrag,
    "scroll": QGraphicsView.ScrollHandDrag,
    "selection": QGraphicsView.RubberBandDrag,
}

# --------------------------------------------------------------------------
# Qt Resource Helpers
# --------------------------------------------------------------------------


def QPen_from_Pen(pen):
    qpen = QPen()
    if pen.color:
        qpen.setColor(get_cached_qcolor(pen.color))
    qpen.setWidth(int(pen.width))
    qpen.setStyle(PEN_STYLES.get(pen.line_style))
    qpen.setCapStyle(CAP_STYLES.get(pen.cap_style))
    qpen.setJoinStyle(JOIN_STYLES.get(pen.join_style))
    if pen.line_style == "custom":
        qpen.setDashPattern(*pen.dash_pattern)
    return qpen


def QBrush_from_Brush(brush):
    qbrush = QBrush()
    if brush.color:
        qbrush.setColor(get_cached_qcolor(brush.color))
    if brush.image:
        qbrush.setTextureImage(get_cached_qimage(brush.image))
        qbrush.setStyle(Qt.TexturePattern)
    else:
        qbrush.setStyle(BRUSH_STYLES.get(brush.style))
    return qbrush


def get_cached_qpen(pen):
    qpen = pen._tkdata
    if not isinstance(qpen, QPen):
        qpen = pen._tkdata = QPen_from_Pen(pen)
    return qpen


def get_cached_qbrush(brush):
    qbrush = brush._tkdata
    if not isinstance(qbrush, QBrush):
        qbrush = brush._tkdata = QBrush_from_Brush(brush)
    return qbrush


# --------------------------------------------------------------------------
# Mixin classes
# --------------------------------------------------------------------------
class FeatureMixin(Atom):
    """A mixin that provides focus and mouse features."""

    #: A private copy of the declaration features. This ensures that
    #: feature cleanup will proceed correctly in the event that user
    #: code modifies the declaration features value at runtime.
    _features = Coerced(Feature, (0,))
    _extra_features = Coerced(GraphicFeature, (0,))

    #: Internal storage for the shared widget action.
    _widget_action = Typed(QWidgetAction)

    #: Internal storage for the drag origin position.
    _drag_origin = Typed(QPointF)

    # --------------------------------------------------------------------------
    # Private API
    # --------------------------------------------------------------------------
    def _setup_features(self):
        """Setup the advanced widget feature handlers."""
        features = self._features = self.declaration.features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.hook_focus_traversal()
        if features & Feature.FocusEvents:
            self.hook_focus_events()
        if features & Feature.DragEnabled:
            self.hook_drag()
        if features & Feature.DropEnabled:
            self.hook_drop()

        features = self._extra_features
        if features & GraphicFeature.WheelEvent:
            self.hook_wheel()
        if features & GraphicFeature.DrawEvent:
            self.hook_draw()

    def _teardown_features(self):
        """Teardowns the advanced widget feature handlers."""
        features = self._features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.unhook_focus_traversal()
        if features & Feature.FocusEvents:
            self.unhook_focus_events()
        if features & Feature.DragEnabled:
            self.unhook_drag()
        if features & Feature.DropEnabled:
            self.unhook_drop()

        features = self._extra_features
        if features & GraphicFeature.WheelEvent:
            self.unhook_wheel()
        if features & GraphicFeature.DrawEvent:
            self.unhook_draw()

    # --------------------------------------------------------------------------
    # Protected API
    # --------------------------------------------------------------------------
    def tab_focus_request(self, reason):
        """Handle a custom tab focus request.

        This method is called when focus is being set on the proxy
        as a result of a user-implemented focus traversal handler.
        This can be reimplemented by subclasses as needed.

        Parameters
        ----------
        reason : Qt.FocusReason
            The reason value for the focus request.

        Returns
        -------
        result : bool
            True if focus was set, False otherwise.

        """
        widget = self.focus_target()
        if not widget.focusPolicy & Qt.TabFocus:
            return False
        if not widget.isEnabled():
            return False
        if not widget.isVisibleTo(widget.window()):
            return False
        widget.setFocus(reason)
        return False

    def focus_target(self):
        """Return the current focus target for a focus request.

        This can be reimplemented by subclasses as needed. The default
        implementation of this method returns the current proxy widget.

        """
        return self.widget

    def hook_focus_traversal(self):
        """Install the hooks for focus traversal.

        This method may be overridden by subclasses as needed.

        """
        self.widget.focusNextPrevChild = self.focusNextPrevChild

    def unhook_focus_traversal(self):
        """Remove the hooks for the next/prev child focusing.

        This method may be overridden by subclasses as needed.

        """
        del self.widget.focusNextPrevChild

    def hook_focus_events(self):
        """Install the hooks for focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        widget.focusInEvent = self.focusInEvent
        widget.focusOutEvent = self.focusOutEvent

    def unhook_focus_events(self):
        """Remove the hooks for the focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        del widget.focusInEvent
        del widget.focusOutEvent

    def focusNextPrevChild(self, next_child):
        """The default 'focusNextPrevChild' implementation."""
        fd = focus_registry.focused_declaration()
        if next_child:
            child = self.declaration.next_focus_child(fd)
            reason = Qt.TabFocusReason
        else:
            child = self.declaration.previous_focus_child(fd)
            reason = Qt.BacktabFocusReason
        if child is not None and child.proxy_is_active:
            return child.proxy.tab_focus_request(reason)
        widget = self.widget
        return type(widget).focusNextPrevChild(widget, next_child)

    def focusInEvent(self, event):
        """The default 'focusInEvent' implementation."""
        widget = self.widget
        type(widget).focusInEvent(widget, event)
        self.declaration.focus_gained()

    def focusOutEvent(self, event):
        """The default 'focusOutEvent' implementation."""
        widget = self.widget
        type(widget).focusOutEvent(widget, event)
        self.declaration.focus_lost()

    def hook_drag(self):
        """Install the hooks for drag operations."""
        widget = self.widget
        widget.mousePressEvent = self.mousePressEvent
        widget.mouseMoveEvent = self.mouseMoveEvent
        widget.mouseReleaseEvent = self.mouseReleaseEvent

    def unhook_drag(self):
        """Remove the hooks for drag operations."""
        widget = self.widget
        del widget.mousePressEvent
        del widget.mouseMoveEvent
        del widget.mouseReleaseEvent

    def mousePressEvent(self, event):
        """Handle the mouse press event for a drag operation."""
        if event.button() == Qt.LeftButton:
            self._drag_origin = event.pos()
        widget = self.widget
        type(widget).mousePressEvent(widget, event)

    def mouseMoveEvent(self, event):
        """Handle the mouse move event for a drag operation."""
        # if event.buttons() & Qt.LeftButton and self._drag_origin is not None:
        # dist = (event.pos() - self._drag_origin).manhattanLength()
        # if dist >= QApplication.startDragDistance():
        # self.do_drag(event.widget())
        # self._drag_origin = None
        # return # Don't returns
        widget = self.widget
        type(widget).mouseMoveEvent(widget, event)

    def mouseReleaseEvent(self, event):
        """Handle the mouse release event for the drag operation."""
        if event.button() == Qt.LeftButton:
            self._drag_origin = None
        widget = self.widget
        type(widget).mouseReleaseEvent(widget, event)

    def hook_drop(self):
        """Install hooks for drop operations."""
        widget = self.widget
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = self.dragEnterEvent
        widget.dragMoveEvent = self.dragMoveEvent
        widget.dragLeaveEvent = self.dragLeaveEvent
        widget.dropEvent = self.dropEvent

    def unhook_drop(self):
        """Remove hooks for drop operations."""
        widget = self.widget
        widget.setAcceptDrops(False)
        del widget.dragEnterEvent
        del widget.dragMoveEvent
        del widget.dragLeaveEvent
        del widget.dropEvent

    def do_drag(self, widget):
        """Perform the drag operation for the widget.

        Parameters
        ----------
        widget: QWidget
            A reference to the viewport widget.

        """
        drag_data = self.declaration.drag_start()
        if drag_data is None:
            return
        # widget = self.widget
        qdrag = QDrag(widget)
        qdrag.setMimeData(drag_data.mime_data.q_data())
        if drag_data.image is not None:
            qimg = get_cached_qimage(drag_data.image)
            qdrag.setPixmap(QPixmap.fromImage(qimg))
        # else:
        # if __version_info__ < (5, ):
        # qdrag.setPixmap(QPixmap.grabWidget(self.widget))
        # else:
        # qdrag.setPixmap(widget.grab())
        if drag_data.hotspot:
            qdrag.setHotSpot(QPoint(*drag_data.hotspot))
        else:
            cursor_position = widget.mapFromGlobal(QCursor.pos())
            qdrag.setHotSpot(cursor_position)
        default = Qt.DropAction(drag_data.default_drop_action)
        supported = Qt.DropActions(drag_data.supported_actions)
        qresult = qdrag.exec_(supported, default)
        self.declaration.drag_end(drag_data, DropAction(int(qresult)))

    def dragEnterEvent(self, event):
        """Handle the drag enter event for the widget."""
        self.declaration.drag_enter(QtDropEvent(event))

    def dragMoveEvent(self, event):
        """Handle the drag move event for the widget."""
        self.declaration.drag_move(QtDropEvent(event))

    def dragLeaveEvent(self, event):
        """Handle the drag leave event for the widget."""
        self.declaration.drag_leave()

    def dropEvent(self, event):
        """Handle the drop event for the widget."""
        self.declaration.drop(QtDropEvent(event))

    def hook_wheel(self):
        """Install the hooks for wheel events."""
        widget = self.widget
        widget.wheelEvent = self.wheelEvent

    def unhook_wheel(self):
        """Removes the hooks for wheel events."""
        widget = self.widget
        del widget.wheelEvent

    def wheelEvent(self, event):
        """Handle the mouse wheel event for the widget."""
        self.declaration.wheel_event(event)

    def hook_draw(self):
        """Remove the hooks for the draw (paint) event.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        widget.paint = self.draw

    def unhook_draw(self):
        """Remove the hooks for the draw (paint) event.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        del widget.paint

    def draw(self, painter, options, widget):
        """Handle the draw event for the widget."""
        self.declaration.draw(painter, options, widget)

    # --------------------------------------------------------------------------
    # Framework API
    # --------------------------------------------------------------------------
    def get_action(self, create=False):
        """Get the shared widget action for this widget.

        This API is used to support widgets in tool bars and menus.

        Parameters
        ----------
        create : bool, optional
            Whether to create the action if it doesn't already exist.
            The default is False.

        Returns
        -------
        result : QWidgetAction or None
            The cached widget action or None, depending on arguments.

        """
        action = self._widget_action
        if action is None and create:
            action = self._widget_action = QWidgetAction(None)
            action.setDefaultWidget(self.widget)
        return action


# --------------------------------------------------------------------------
# Toolkit implementations
# --------------------------------------------------------------------------
class QtGraphicsView(QtControl, ProxyGraphicsView):
    #: Internal widget
    widget = Typed(QGraphicsView)

    #: Internal scene
    scene = Typed(QGraphicsScene)

    #: View Range
    view_range = Typed(QRectF, (0, 0, 1, 1))

    #: Custom features
    _extra_features = Coerced(GraphicFeature, (0,))

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guards = Int(0)

    def create_widget(self):
        self.scene = QGraphicsScene()
        self.widget = QGraphicsView(self.scene, self.parent_widget())

    def init_widget(self):
        d = self.declaration
        self._extra_features = d.extra_features
        super(QtGraphicsView, self).init_widget()

        widget = self.widget
        widget.setCacheMode(QGraphicsView.CacheBackground)
        widget.setFocusPolicy(Qt.StrongFocus)
        widget.setFrameShape(QFrame.NoFrame)
        widget.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        widget.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        widget.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        widget.setMouseTracking(True)

        self.set_drag_mode(d.drag_mode)
        self.set_renderer(d.renderer)
        self.set_antialiasing(d.antialiasing)
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def init_layout(self):
        super(QtGraphicsView, self).init_layout()
        scene = self.scene
        for item in self.scene_items():
            scene.addItem(item)

        self.set_view_range(self.view_range)

    def child_added(self, child):
        if isinstance(child, QtGraphicsItem):
            self.scene.addItem(child.widget)
        else:
            super(QtGraphicsView, self).child_added(child)

    def child_removed(self, child):
        if isinstance(child, QtGraphicsItem):
            self.scene.removeItem(child.widget)
        else:
            super(QtGraphicsView, self).child_removed(child)

    def scene_items(self):
        for w in self.children():
            if isinstance(w, QtGraphicsItem):
                yield w.widget

    # --------------------------------------------------------------------------
    # GraphicFeature API
    # --------------------------------------------------------------------------
    def _setup_features(self):
        super(QtGraphicsView, self)._setup_features()
        features = self._extra_features
        if features & GraphicFeature.MouseEvent:
            self.hook_drag()
        if features & GraphicFeature.WheelEvent:
            self.hook_wheel()
        self.hook_resize()

    def _teardown_features(self):
        super(QtGraphicsView, self)._teardown_features()
        features = self._extra_features
        if features & GraphicFeature.MouseEvent:
            self.unhook_drag()
        if features & GraphicFeature.WheelEvent:
            self.unhook_wheel()
        self.unhook_resize()

    def hook_wheel(self):
        """Install the hooks for wheel events."""
        widget = self.widget
        widget.wheelEvent = self.wheelEvent

    def unhook_wheel(self):
        """Removes the hooks for wheel events."""
        widget = self.widget
        del widget.wheelEvent

    def hook_draw(self):
        """Install the hooks for background draw events."""
        widget = self.widget
        widget.drawBackground = self.drawBackground

    def unhook_draw(self):
        """Removes the hooks for background draw events."""
        widget = self.widget
        del widget.drawBackground

    def hook_resize(self):
        """Install the hooks for resize events."""
        widget = self.widget
        widget.resizeEvent = self.resizeEvent

    def unhook_resize(self):
        """Removes the hooks for resize events."""
        widget = self.widget
        del widget.resizeEvent

    # --------------------------------------------------------------------------
    # QGraphicView API
    # --------------------------------------------------------------------------
    def wheelEvent(self, event):
        """Handle the wheel event for the widget."""
        self.declaration.wheel_event(event)

    def drawBackground(self, painter, rect):
        """Handle the drawBackground request"""
        self.declaration.draw_background(painter, rect)

    def mousePressEvent(self, event):
        """Handle the mouse press event for a drag operation."""
        self.declaration.mouse_press_event(event)
        super(QtGraphicsView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle the mouse move event for a drag operation."""
        self.declaration.mouse_move_event(event)
        super(QtGraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle the mouse release event for the drag operation."""
        self.declaration.mouse_release_event(event)
        super(QtGraphicsView, self).mouseReleaseEvent(event)

    def resizeEvent(self, event):
        """Resize the view range to match the widget size"""
        d = self.declaration
        widget = self.widget

        if d.auto_range:
            size = self.widget.size()
            view_range = QRectF(0, 0, size.width(), size.height())
            # view_range = self.scene.itemsBoundingRect()
        else:
            # Return the boundaries of the view in scene coordinates
            r = QRectF(widget.rect())
            view_range = widget.viewportTransform().inverted()[0].mapRect(r)
        self.set_view_range(view_range)

    # --------------------------------------------------------------------------
    # ProxyGraphicsView API
    # --------------------------------------------------------------------------
    def set_view_range(self, view_range):
        """Set the visible scene rect to override the default behavior
        of limiting panning and viewing to the graphics items view.

        Based on Luke Campagnola's updateMatrix of pyqtgraph's GraphicsView

        """
        d = self.declaration
        self.view_range = view_range
        widget = self.widget
        widget.setSceneRect(view_range)
        if d.auto_range:
            widget.resetTransform()
        else:
            if d.lock_aspect_ratio:
                flags = Qt.KeepAspectRatio
            else:
                flags = Qt.IgnoreAspectRatio
            widget.fitInView(view_range, flags)

    def set_drag_mode(self, mode):
        self.widget.setDragMode(DRAG_MODES.get(mode))

    def set_auto_range(self, enabled):
        self.set_view_range(self.view_range)

    def set_lock_aspect_ratio(self, locked):
        self.set_view_range(self.view_range)

    def set_antialiasing(self, enabled):
        flags = self.widget.renderHints()
        if enabled:
            flags |= QPainter.Antialiasing
        else:
            flags &= ~QPainter.Antialiasing
        self.widget.setRenderHints(flags)

    def set_renderer(self, renderer):
        """Set the viewport widget."""
        viewport = None
        if renderer == "opengl":
            from enaml.qt.QtWidgets import QOpenGLWidget

            viewport = QOpenGLWidget()
        elif renderer == "default":
            try:
                from enaml.qt.QtWidgets import QOpenGLWidget

                viewport = QOpenGLWidget()
            except ImportError as e:
                warnings.warn("QOpenGLWidget could not be imported: {}".format(e))
        self.widget.setViewport(viewport)

    def set_selected_items(self, items):
        if self._guards & 0x01:
            return
        self.scene.clearSelection()
        for item in items:
            item.selected = True

    def on_selection_changed(self):
        """Callback invoked one the selection has changed."""
        d = self.declaration
        selection = self.scene.selectedItems()
        self._guards |= 0x01
        try:
            d.selected_items = [
                item.ref().declaration for item in selection if item.ref()
            ]
        finally:
            self._guards &= ~0x01

    def set_background(self, background):
        """Set the background color of the widget."""
        scene = self.scene
        scene.setBackgroundBrush(QColor.fromRgba(background.argb))

    def get_item_at(self, point):
        item = self.scene.getItemAt(point.x, point.y)
        if item and item.ref():
            return item.ref().declaration

    def get_items_at(self, point):
        items = self.scene.items(point.x, point.y)
        return [item.ref().declaration for item in items if item.ref()]

    def get_items_in(self, top_left, bottom_right):
        qrect = QRectF(
            QPointF(top_left.x, top_left.y), QPointF(bottom_right.x, bottom_right.y)
        )
        items = self.scene.items(qrect)
        return [item.ref().declaration for item in items if item.ref()]

    def fit_in_view(self, item):
        self.widget.fitInView(item.proxy.widget)

    def center_on(self, item):
        if isinstance(item, Point):
            self.widget.centerOn(item.x, item.y)
        else:
            self.widget.centerOn(item.proxy.widget)

    def reset_view(self):
        self.widget.resetTransform()

    def translate_view(self, x, y):
        view_range = self.view_range.adjusted(x, y, x, y)
        self.set_view_range(view_range)
        return view_range

    def scale_view(self, x, y):
        """Scale the zoom but keep in in the min and max zoom bounds."""
        d = self.declaration
        sx, sy = float(x), float(y)
        if d.lock_aspect_ratio:
            sy = sx
        view_range = self.view_range
        center = view_range.center()
        w, h = view_range.width() / sx, view_range.height() / sy
        cx, cy = center.x(), center.y()
        x = cx - (cx - view_range.left()) / sx
        y = cy - (cy - view_range.top()) / sy
        view_range = QRectF(x, y, w, h)
        self.set_view_range(view_range)
        return view_range

    def rotate_view(self, angle):
        self.widget.rotate(angle)

    def map_from_scene(self, point):
        qpoint = self.widget.mapFromScene(point.x, point.y)
        return Point(qpoint.x(), qpoint.y())

    def map_to_scene(self, point):
        qpoint = self.widget.mapToScene(point.x, point.y)
        return Point(qpoint.x(), qpoint.y())

    def pixel_density(self):
        tr = self.widget.transform().inverted()[0]
        p = tr.map(QPoint(1, 1)) - tr.map(QPoint(0, 0))
        return Point(p.x(), p.y())


class QtGraphicsItem(QtToolkitObject, ProxyGraphicsItem, FeatureMixin):
    """QtGraphicsItem is essentially a copy of QtWidget except that
    it uses `self.widget`, `create_widget` and `init_widget` instead of
    widget.

    """

    #: Internal item
    widget = Typed(QGraphicsObject)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    #: 0x01 is position
    _guards = Int(0)

    # --------------------------------------------------------------------------
    # Initialization API
    # --------------------------------------------------------------------------
    def create_widget(self):
        self.widget = QGraphicsObject(self.parent_widget())

    def init_widget(self):
        widget = self.widget

        # Save a reference so we can retrieve the QtGraphicsItem
        # from the QGraphicsItem
        widget.ref = atomref(self)

        focus_registry.register(widget, self)
        d = self.declaration
        self._extra_features = d.extra_features
        self._setup_features()

        if d.selectable:
            self.set_selectable(d.selectable)
        if d.movable:
            self.set_movable(d.movable)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        if not d.enabled:
            self.set_enabled(d.enabled)
        if not d.visible:
            self.set_visible(d.visible)
        if d.opacity != 1:
            self.set_opacity(d.opacity)
        if d.rotation:
            self.set_rotation(d.rotation)
        if d.scale != 1:
            self.set_scale(d.scale)
        self.set_position(d.position)
        self.hook_item_change()

    def init_layout(self):
        pass

    # --------------------------------------------------------------------------
    # ProxyToolkitObject API
    # --------------------------------------------------------------------------
    def destroy(self):
        """Destroy the underlying QWidget object."""
        self._teardown_features()
        focus_registry.unregister(self.widget)
        widget = self.widget
        if widget is not None:
            del self.widget
        super(QtGraphicsItem, self).destroy()
        # If a QWidgetAction was created for this widget, then it has
        # taken ownership of the widget and the widget will be deleted
        # when the QWidgetAction is garbage collected. This means the
        # superclass destroy() method must run before the reference to
        # the QWidgetAction is dropped.
        del self._widget_action

    def parent_widget(self):
        """Reimplemented to only return GraphicsItems"""
        parent = self.parent()
        if parent is not None and isinstance(parent, QtGraphicsItem):
            return parent.widget

    def _teardown_features(self):
        super(QtGraphicsItem, self)._teardown_features()
        self.unhook_item_change()

    def hook_item_change(self):
        widget = self.widget
        widget.itemChange = self.itemChange

    def unhook_item_change(self):
        del self.widget.itemChange

    # --------------------------------------------------------------------------
    # Signals
    # --------------------------------------------------------------------------
    def itemChange(self, change, value):
        widget = self.widget
        if change == QGraphicsItem.ItemPositionHasChanged:
            pos = widget.pos()
            pos = Point(pos.x(), pos.y(), widget.zValue())
            self._guards |= 0x01
            try:
                self.declaration.position = pos
            finally:
                self._guards &= ~0x01
        elif change == QGraphicsItem.ItemSelectedChange:
            self.declaration.selected = widget.isSelected()

        return type(widget).itemChange(widget, change, value)

    # --------------------------------------------------------------------------
    # ProxyGraphicsItem API
    # --------------------------------------------------------------------------
    def set_visible(self, visible):
        self.widget.setVisible(visible)

    def set_enabled(self, enabled):
        self.widget.setEnabled(enabled)

    def set_selectable(self, enabled):
        self.widget.setFlag(QGraphicsItem.ItemIsSelectable, enabled)

    def set_movable(self, enabled):
        self.widget.setFlag(QGraphicsItem.ItemIsMovable, enabled)

    def set_x(self, x):
        if self._guards & 0x01:
            return
        self.widget.setX(x)

    def set_y(self, y):
        if self._guards & 0x01:
            return
        self.widget.setY(y)

    def set_z(self, z):
        if self._guards & 0x01:
            return
        self.widget.setZValue(z)

    def set_position(self, position):
        if self._guards & 0x01:
            return
        pos = self.declaration.position
        w = self.widget
        w.setPos(pos.x, pos.y)
        w.setZValue(pos.z)

    def set_rotation(self, rotation):
        self.widget.setRotation(rotation)

    def set_scale(self, scale):
        self.widget.setScale(scale)

    def set_opacity(self, opacity):
        self.widget.setOpacity(opacity)

    def set_selected(self, selected):
        self.widget.setSelected(selected)

    def set_tool_tip(self, tool_tip):
        self.widget.setToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        self.widget.setToolTip(status_tip)


class QtGraphicsItemGroup(QtGraphicsItem, ProxyGraphicsItemGroup):
    #: Internal widget
    widget = Typed(QGraphicsItemGroup)

    def create_widget(self):
        self.widget = QGraphicsItemGroup(self.parent_widget())

    def init_layout(self):
        super(QtGraphicsItemGroup, self).init_layout()
        widget = self.widget
        for item in self.child_widgets():
            widget.addToGroup(item)

    def child_added(self, child):
        super(QtGraphicsItemGroup, self).child_added(child)
        if isinstance(child, QtGraphicsItem):
            self.widget.addToGroup(child.widget)

    def child_removed(self, child):
        super(QtGraphicsItemGroup, self).child_removed(child)
        if isinstance(child, QtGraphicsItem):
            self.widget.removeFromGroup(child.widget)


class QtGraphicsWidget(QtGraphicsItem, ProxyGraphicsWidget):
    #: Internal widget
    widget = Typed(QGraphicsProxyWidget)

    def create_widget(self):
        """Deferred to the layout pass"""
        pass

    def init_widget(self):
        pass

    def init_layout(self):
        """Create the widget in the layout pass after the child widget has
        been created and intialized. We do this so the child widget does not
        attempt to use this proxy widget as its parent and because
        repositioning must be done after the widget is set.
        """
        self.widget = QGraphicsProxyWidget(self.parent_widget())
        widget = self.widget
        for item in self.child_widgets():
            widget.setWidget(item)
            break
        super(QtGraphicsWidget, self).init_widget()
        super(QtGraphicsWidget, self).init_layout()

    def child_added(self, child):
        super(QtGraphicsItemGroup, self).child_added(child)
        if isinstance(child, QtWidget):
            self.widget.setWidget(child.widget)


class QtAbstractGraphicsShapeItem(QtGraphicsItem, ProxyAbstractGraphicsShapeItem):
    def init_widget(self):
        super(QtAbstractGraphicsShapeItem, self).init_widget()
        d = self.declaration
        if d.pen:
            self.set_pen(d.pen)
        if d.brush:
            self.set_brush(d.brush)

    def set_pen(self, pen):
        if pen:
            self.widget.setPen(get_cached_qpen(pen))
        else:
            self.widget.setPen(QPen())

    def set_brush(self, brush):
        if brush:
            self.widget.setBrush(get_cached_qbrush(brush))
        else:
            self.widget.setBrush(QBrush())


class QtGraphicsLineItem(QtAbstractGraphicsShapeItem, ProxyGraphicsLineItem):
    #: Internal widget
    widget = Typed(QGraphicsLineItem)

    def create_widget(self):
        self.widget = QGraphicsLineItem(self.parent_widget())

    def set_position(self, position):
        self.set_point(self.declaration.point)

    def set_point(self, point):
        pos = self.declaration.position
        self.widget.setLine(pos.x, pos.y, *point[:2])


class QtGraphicsEllipseItem(QtAbstractGraphicsShapeItem, ProxyGraphicsEllipseItem):
    #: Internal widget
    widget = Typed(QGraphicsEllipseItem)

    def create_widget(self):
        self.widget = QGraphicsEllipseItem(self.parent_widget())

    def init_widget(self):
        super(QtGraphicsEllipseItem, self).init_widget()
        d = self.declaration
        self.set_start_angle(d.start_angle)
        self.set_span_angle(d.span_angle)

    def set_position(self, position):
        self.update_rect()

    def set_width(self, width):
        self.update_rect()

    def set_height(self, height):
        self.update_rect()

    def update_rect(self):
        d = self.declaration
        pos = d.position
        self.widget.setRect(pos.x, pos.y, d.width, d.height)

    def set_span_angle(self, angle):
        self.widget.setSpanAngle(int(angle * 16))

    def set_start_angle(self, angle):
        self.widget.setStartAngle(int(angle * 16))


class QtGraphicsRectItem(QtAbstractGraphicsShapeItem, ProxyGraphicsRectItem):
    #: Internal widget
    widget = Typed(QGraphicsRectItem)

    def create_widget(self):
        self.widget = QGraphicsRectItem(self.parent_widget())

    def set_position(self, position):
        self.update_rect()

    def set_width(self, width):
        self.update_rect()

    def set_height(self, height):
        self.update_rect()

    def update_rect(self):
        d = self.declaration
        pos = d.position
        self.widget.setRect(pos.x, pos.y, d.width, d.height)


class QtGraphicsTextItem(QtAbstractGraphicsShapeItem, ProxyGraphicsTextItem):
    #: Internal widget
    widget = Typed(QGraphicsSimpleTextItem)

    def create_widget(self):
        self.widget = QGraphicsSimpleTextItem(self.parent_widget())

    def init_widget(self):
        super(QtGraphicsTextItem, self).init_widget()
        d = self.declaration
        if d.text:
            self.set_text(d.text)
        if d.font:
            self.set_font(d.font)

    def set_text(self, text):
        self.widget.setText(text)

    def set_font(self, font):
        self.widget.setFont(get_cached_qfont(font))


class QtGraphicsPolygonItem(QtAbstractGraphicsShapeItem, ProxyGraphicsPolygonItem):
    #: Internal widget
    widget = Typed(QGraphicsPolygonItem)

    def create_widget(self):
        self.widget = QGraphicsPolygonItem(self.parent_widget())

    def init_widget(self):
        super(QtGraphicsPolygonItem, self).init_widget()
        d = self.declaration
        self.set_points(d.points)

    def set_points(self, points):
        polygon = QPolygonF([QPointF(*p[:2]) for p in points])
        self.widget.setPolygon(polygon)


class QtGraphicsPathItem(QtAbstractGraphicsShapeItem, ProxyGraphicsPathItem):
    #: Internal widget
    widget = Typed(QGraphicsPathItem)

    def create_widget(self):
        self.widget = QGraphicsPathItem(self.parent_widget())

    def init_widget(self):
        super(QtGraphicsPathItem, self).init_widget()
        d = self.declaration
        if d.path:
            self.set_path(d.path)

    def set_path(self, path):
        #: TODO: Convert path
        self.widget.setPath(path)


class QtGraphicsImageItem(QtGraphicsItem, ProxyGraphicsImageItem):
    #: Internal widget
    widget = Typed(QGraphicsPixmapItem)

    def create_widget(self):
        self.widget = QGraphicsPixmapItem(self.parent_widget())

    def init_widget(self):
        super(QtGraphicsImageItem, self).init_widget()
        d = self.declaration
        if d.image:
            self.set_image(d.image)

    def set_image(self, image):
        self.widget.setPixmap(QPixmap.fromImage(get_cached_qimage(image)))
