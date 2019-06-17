"""
Copyright (c) 2018, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Sept 5, 2018
"""
import sys
from atom.api import (
    Atom, Float, Int, Typed, Bool, Coerced, ForwardTyped, Enum, List, IntEnum,
    Instance, Unicode, Value, Event, Property, observe, set_default
)
from enaml.colors import ColorMember
from enaml.core.declarative import d_, d_func
from enaml.fonts import FontMember
from enaml.image import Image
from enaml.layout.constrainable import ConstrainableMixin, PolicyEnum
from enaml.widgets.widget import Feature
from enaml.widgets.control import Control, ProxyControl
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject


NUMERIC = (int, float, long) if sys.version_info.major < 3 else (int, float)


class GraphicFeature(IntEnum):
    #: Enables support for mouse events.
    MouseEvent = 0x08
    
    #: Enables support for wheel events.
    WheelEvent = 0x16
    
    #: Enables support for draw or paint events.
    DrawEvent = 0x32
    
    #: Enables support for backgound draw events.
    BackgroundDrawEvent = 0x64




class Point(Atom):
    #: x position
    x = d_(Float(0, strict=False))
    
    #: y position
    y = d_(Float(0, strict=False))
    
    #: z position
    z = d_(Float(0, strict=False))
    
    def __init__(self, x=0, y=0, z=0):
        super(Point, self).__init__(x=x, y=y, z=z)
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
    
    def __len__(self):
        return 3
    
    def __eq__(self, other):
        pos = (self.x, self.y, self.z)
        if isinstance(other, Point):
            return pos == (other.x, other.y, other.z)
        return pos == other
    
    def __add__(self, other):
        return Point(self.x + other[0],
                     self.y + other[1],
                     self.z + other[2] if len(other) > 2 else self.z)
    __radd__ = __add__

    def __sub__(self, other):
        return Point(self.x - other[0],
                     self.y - other[1],
                     self.z - other[2] if len(other) > 2 else self.z)
    
    def __rsub__(self, other):
        return Point(other[0] - self.x,
                     other[1] - self.y,
                     other[2] - self.z if len(other) > 2 else self.z)
    
    def __mul__(self, other):
        if isinstance(other, NUMERIC):
            return Point(self.x*other, self.y*other, self.z*other)
        return Point(other[0] * self.x,
                     other[1] * self.y,
                     other[2] * self.z if len(other) > 2 else self.z)
    __rmul__ = __mul__
    
    def __div__(self, other):
        if isinstance(other, NUMERIC):
            return Point(self.x/other, self.y/other, self.z/other)
        return Point(self.x/other[0],
                     self.y/other[1],
                     self.z/other[2] if len(other) > 2 else self.z)
    
    def __rdiv__(self, other):
        if isinstance(other, NUMERIC):
            return Point(other/self.x, other/self.y, other/self.z)
        return Point(other[0]/self.x,
                     other[1]/self.y,
                     other[2]/self.z if len(other) > 2 else self.z)
    
    def __neg__(self):
        return Point(-self.x, -self.y, -self.z)

    def __hash__(self):
        return id(self)
    
    def __getitem__(self, key):
        return (self.x, self.y, self.z)[key]
    
    def __repr__(self):
        return "Point(%d, %d, %d)"%(self.x, self.y, self.z)
        

class Rect(Atom):
    x = d_(Float(0, strict=False))
    y = d_(Float(0, strict=False))
    width = d_(Float(0, strict=False))
    height = d_(Float(0, strict=False))


def coerce_point(p):
    return p if isinstance(p, Point) else Point(*p)
    

class PointMember(Coerced):
    def __init__(self, args=None, kwargs=None, factory=None, 
                 coercer=coerce_point):
        super(PointMember, self).__init__(
            Point, args, kwargs, factory, coercer)


class Pen(Atom):
    #: Color
    color = ColorMember()
    
    #: Width
    width = Float(1.0, strict=False)
    
    #: Line Style
    line_style = Enum('solid', 'dash', 'dot', 'dash_dot', 'dash_dot_dot',
                      'custom', 'none')
    
    #: Cap Style
    cap_style = Enum('square', 'flat', 'round')
    
    #: Join Style
    join_style = Enum('bevel', 'miter', 'round')
    
    #: Dash pattern used when line_style is 'custom'
    dash_pattern = List(Float(strict=False))
    
    #: Internal data
    _tkdata = Value()
    

class Brush(Atom):
    """ Defines the fill pattern """
    #: Color
    color = ColorMember()
    
    #: Image
    image = Instance(Image)
    
    #: Style
    style = Enum('solid', 'dense1', 'dense2', 'dense3', 'dense4', 'dense5',
                 'dense6', 'dense7', 'horizontal', 'vertical', 'cross',
                 'diag', 'bdiag', 'fdiag', 'linear', 'radial', 'conical',
                 'texture', 'none')
    
    #: Internal data
    _tkdata = Value()
    

class ProxyGraphicsView(ProxyControl):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsView)
    
    def set_auto_range(self, enabled):
        raise NotImplementedError
    
    def set_antialiasing(self, enabled):
        raise NotImplementedError    
    
    def set_drag_mode(self, mode):
        raise NotImplementedError
    
    def set_renderer(self, renderer):
        raise NotImplementedError
    
    def get_item_at(self, point):
        raise NotImplementedError
    
    def set_lock_aspect_ratio(self, locked):
        raise NotImplementedError
    
    def set_selected_items(self, items):
        raise NotImplementedError
    
    def fit_in_view(self, item):
        raise NotImplementedError
    
    def center_on(self, item):
        raise NotImplementedError
    
    def reset_view(self):
        raise NotImplementedError
    
    def translate_view(self, x, y):
        raise NotImplementedError
    
    def scale_view(self, x, y):
        raise NotImplementedError
    
    def rotate_view(self, angle):
        raise NotImplementedError
    
    def map_from_scene(self, point):
        raise NotImplementedError
    
    def map_to_scene(self, point):
        raise NotImplementedError
    
    def pixel_density(self):
        raise NotImplementedError
    

class ProxyGraphicsItem(ProxyToolkitObject):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsItem)
    
    def set_x(self, x):
        raise NotImplementedError
    
    def set_y(self, y):
        raise NotImplementedError
    
    def set_z(self, z):
        raise NotImplementedError
    
    def set_position(self, position):
        raise NotImplementedError
    
    def set_rotation(self, rotation):
        raise NotImplementedError
    
    def set_scale(self, scale):
        raise NotImplementedError
    
    def set_opacity(self, opacity):
        raise NotImplementedError
    
    def set_selected(self, selected):
        raise NotImplementedError
    
    def set_enabled(self, enabled):
        raise NotImplementedError
    
    def set_selectable(self, enabled):
        raise NotImplementedError
    
    def set_movable(self, enabled):
        raise NotImplementedError
    
    def set_visible(self, visible):
        raise NotImplementedError
    
    def set_tool_tip(self, tool_tip):
        raise NotImplementedError
    
    def set_status_tip(self, status_tip):
        raise NotImplementedError
    
    def request_update(self):
        raise NotImplementedError
    
    def ensure_visible(self):
        raise NotImplementedError

    def ensure_hidden(self):
        raise NotImplementedError

    def set_focus(self):
        raise NotImplementedError

    def clear_focus(self):
        raise NotImplementedError

    def has_focus(self):
        raise NotImplementedError


class ProxyGraphicsItemGroup(ProxyGraphicsItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsItemGroup)
    

class ProxyGraphicsWidget(ProxyGraphicsItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsWidget)
    

class ProxyAbstractGraphicsShapeItem(ProxyGraphicsItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: AbstractGraphicsShapeItem)
    
    def set_pen(self, pen):
        raise NotImplementedError
    
    def set_brush(self, brush):
        raise NotImplementedError


class ProxyGraphicsRectItem(ProxyAbstractGraphicsShapeItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsRectItem)
    
    def set_width(self, width):
        raise NotImplementedError
    
    def set_height(self, height):
        raise NotImplementedError


class ProxyGraphicsEllipseItem(ProxyAbstractGraphicsShapeItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsEllipseItem)
    
    def set_width(self, width):
        raise NotImplementedError
    
    def set_height(self, height):
        raise NotImplementedError
    
    def set_span_angle(self, angle):
        raise NotImplementedError
    
    def set_start_angle(self, angle):
        raise NotImplementedError
    

class ProxyGraphicsLineItem(ProxyAbstractGraphicsShapeItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsLineItem)
    
    def set_point(self, point):
        raise NotImplementedError


class ProxyGraphicsTextItem(ProxyAbstractGraphicsShapeItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsTextItem)
    
    def set_text(self, text):
        raise NotImplementedError
    
    def set_font(self, font):
        raise NotImplementedError


class ProxyGraphicsPolygonItem(ProxyAbstractGraphicsShapeItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsPolygonItem)
    
    def set_points(self, points):
        raise NotImplementedError    
    
    
class ProxyGraphicsPathItem(ProxyAbstractGraphicsShapeItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsPathItem)
    
    def set_path(self, path):
        raise NotImplementedError


class ProxyGraphicsImageItem(ProxyGraphicsItem):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: GraphicsImageItem)
    
    def set_image(self, image):
        raise NotImplementedError


class GraphicsItem(ToolkitObject, ConstrainableMixin):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsItem)
    
    # --------------------------------------------------------------------------
    # Item orentation
    # --------------------------------------------------------------------------
    #: Position
    position = d_(PointMember())
    
    #: Item rotation
    rotation = d_(Float(strict=False))

    #: Item scale
    scale = d_(Float(1.0, strict=False))
    
    # --------------------------------------------------------------------------
    # Item display
    # --------------------------------------------------------------------------
    
    #: Item opacity
    opacity = d_(Float(1.0, strict=False))
    
    # Item selected
    selected = d_(Bool())
    
    # Item is enabled
    enabled = d_(Bool(True))
    
    # Item is visible
    visible = d_(Bool(True))
    
    #: Tool tip
    tool_tip = d_(Unicode())
    
    #: Status tip
    status_tip = d_(Unicode())
    
    # --------------------------------------------------------------------------
    # Item interaction
    # --------------------------------------------------------------------------
    
    #: Set the extra features to enable for this widget. This value must
    #: be provided when the widget is instantiated. Runtime changes to
    #: this value are ignored.
    features = d_(Coerced(Feature.Flags))
    extra_features = d_(Coerced(GraphicFeature.Flags))

    #: Update
    request_update = d_(Event())
    
    #: Set whether this item can be selected.
    selectable = d_(Bool())
    
    #: Set whether this item can be moved.
    movable = d_(Bool())
    
    @observe('position', 'position.x', 'position.y', 'position.z', 'scale', 
             'rotation', 'opacity',  'selected', 'enabled', 'visible', 
             'tool_tip', 'status_tip', 'request_update', 'selectable',
             'movable')
    def _update_proxy(self, change):
        super(GraphicsItem, self)._update_proxy(change)
    
    # --------------------------------------------------------------------------
    # Widget API
    # --------------------------------------------------------------------------
    def show(self):
        """ Ensure the widget is shown.
        Calling this method will also set the widget visibility to True.
        """
        self.visible = True
        if self.proxy_is_active:
            self.proxy.ensure_visible()

    def hide(self):
        """ Ensure the widget is hidden.
        Calling this method will also set the widget visibility to False.
        """
        self.visible = False
        if self.proxy_is_active:
            self.proxy.ensure_hidden()
            
    def set_focus(self):
        """ Set the keyboard input focus to this widget.
        FOR ADVANCED USE CASES ONLY: DO NOT ABUSE THIS!
        """
        if self.proxy_is_active:
            self.proxy.set_focus()

    def clear_focus(self):
        """ Clear the keyboard input focus from this widget.
        FOR ADVANCED USE CASES ONLY: DO NOT ABUSE THIS!
        """
        if self.proxy_is_active:
            self.proxy.clear_focus()

    def has_focus(self):
        """ Test whether this widget has input focus.
        FOR ADVANCED USE CASES ONLY: DO NOT ABUSE THIS!
        Returns
        -------
        result : bool
            True if this widget has input focus, False otherwise.
        """
        if self.proxy_is_active:
            return self.proxy.has_focus()
        return False

    @d_func
    def focus_gained(self):
        """ A method invoked when the widget gains input focus.
        ** The FocusEvents feature must be enabled for the widget in
        order for this method to be called. **
        """
        pass

    @d_func
    def focus_lost(self):
        """ A method invoked when the widget loses input focus.
        ** The FocusEvents feature must be enabled for the widget in
        order for this method to be called. **
        """
        pass

    @d_func
    def drag_start(self):
        """ A method called at the start of a drag-drop operation.
        This method is called when the user starts a drag operation
        by dragging the widget with the left mouse button. It returns
        the drag data for the drag operation.
        ** The DragEnabled feature must be enabled for the widget in
        order for this method to be called. **
        Returns
        -------
        result : DragData
            An Enaml DragData object which holds the drag data. If
            this is not provided, no drag operation will occur.
        """
        return None

    @d_func
    def drag_end(self, drag_data, result):
        """ A method called at the end of a drag-drop operation.
        This method is called after the user has completed the drop
        operation by releasing the left mouse button. It is passed
        the original drag data object along with the resulting drop
        action of the operation.
        ** The DragEnabled feature must be enabled for the widget in
        order for this method to be called. **
        Parameters
        ----------
        data : DragData
            The drag data created by the `drag_start` method.
        result : DropAction
            The requested drop action when the drop completed.
        """
        pass

    @d_func
    def drag_enter(self, event):
        """ A method invoked when a drag operation enters the widget.
        The widget should inspect the mime data of the event and
        accept the event if it can handle the drop action. The event
        must be accepted in order to receive further drag-drop events.
        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **
        Parameters
        ----------
        event : DropEvent
            The event representing the drag-drop operation.
        """
        pass

    @d_func
    def drag_move(self, event):
        """ A method invoked when a drag operation moves in the widget.
        This method will not normally be implemented, but it can be
        useful for supporting advanced drag-drop interactions.
        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **
        Parameters
        ----------
        event : DropEvent
            The event representing the drag-drop operation.
        """
        pass

    @d_func
    def drag_leave(self):
        """ A method invoked when a drag operation leaves the widget.
        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **
        """
        pass

    @d_func
    def drop(self, event):
        """ A method invoked when the user drops the data on the widget.
        The widget should either accept the proposed action, or set
        the drop action to an appropriate action before accepting the
        event, or set the drop action to DropAction.Ignore and then
        ignore the event.
        ** The DropEnabled feature must be enabled for the widget in
        order for this method to be called. **
        Parameters
        ----------
        event : DropEvent
            The event representing the drag-drop operation.
        """
        pass
    
    @d_func
    def mouse_press_event(self, event):
        """ A method invoked when a mouse press event occurs in the widget.
        
        ** The MouseEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : MouseEvent
            The event representing the press operation.
        """
        pass
    
    @d_func
    def mouse_move_event(self, event):
        """ A method invoked when a mouse move event occurs in the widget.
        
        ** The MouseEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : MouseEvent
            The event representing the press operation.
        """
        pass
    
    @d_func
    def mouse_release_event(self, event):
        """ A method invoked when a mouse release event occurs in the widget.
        
        ** The MouseEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : MouseEvent
            The event representing the press operation.
        """
        pass
    
    @d_func
    def wheel_event(self, event):
        """ A method invoked when a wheel event occurs in the widget.
        This method will not normally be implemented, but it can be
        useful for supporting zooming and other scolling interactions.
        
        ** The WheelEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : WheelEvent
            The event representing the wheel operation.
        """
        pass
    
    @d_func
    def draw(self, painter, options, widget):
        """ A method invoked when this widget needs to be drawn.
        This method will not normally be implemented, but it can be
        useful for creating custom graphics.
        
        ** The DrawEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        painter: Object
            The toolkit dependent painter object.
        options: Object
            The toolkit dependent options object.
        widget: Widget
            The underlying widget.
        """
        pass
    

class GraphicsView(Control):
    
    #: Proxy reference
    proxy = Typed(ProxyGraphicsView)
    
    #: An graphicsview widget expands freely in height and width by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')
    
    #: Select backend for rendering. OpenGL is used by default if available.
    renderer = d_(Enum('default', 'opengl', 'qwidget'))
    
    #: Antialiasing is enabled by default. If performance is an issue, disable
    #: this.
    antialiasing = d_(Bool(True))
    
    #: Items currently selected
    selected_items = d_(List(GraphicsItem))
    
    #: Defines the behavior when dragging. By default nothing is done. Pan
    #: will pan the scene around and selection will draw a box to select items.
    drag_mode = d_(Enum('none', 'scroll', 'selection'))
    
    #: Range of allowed zoom factors. This is used to prevent scaling way out
    #: or way in by accident. 
    min_zoom = d_(Float(0.007, strict=False))
    max_zoom = d_(Float(100.0, strict=False))
    
    #: Automatically resize view to fit the scene contents
    auto_range = d_(Bool(False)) # TODO: Broken
    
    #: Keep the aspect ratio locked when resizing the view range 
    lock_aspect_ratio = d_(Bool(True))
    
    #: Set the extra features to enable for this widget. This value must
    #: be provided when the widget is instantiated. Runtime changes to
    #: this value are ignored.
    extra_features = d_(Coerced(GraphicFeature.Flags))
    
    def _default_extra_features(self):
        return GraphicFeature.WheelEvent | GraphicFeature.MouseEvent
    
    @observe('selected_items', 'renderer', 'antialiasing', 'drag_mode', 
             'auto_range', 'lock_aspect_ratio')
    def _update_proxy(self, change):
        super(GraphicsView, self)._update_proxy(change)
    
    # --------------------------------------------------------------------------
    # Widget API
    # --------------------------------------------------------------------------
    @d_func
    def wheel_event(self, event):
        """ A method invoked when a wheel event occurs in the widget.
        This method will not normally be implemented, but it can be
        useful for supporting zooming and other scolling interactions.
        
        ** The WheelEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : WheelEvent
            The event representing the wheel operation.
        """
        pass
        
    @d_func
    def mouse_press_event(self, event):
        """ A method invoked when a mouse press event occurs in the widget.
        
        ** The MouseEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : MouseEvent
            The event representing the press operation.
        """
        pass
    
    @d_func
    def mouse_move_event(self, event):
        """ A method invoked when a mouse move event occurs in the widget.
        
        ** The MouseEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : MouseEvent
            The event representing the press operation.
        """
        pass
    
    @d_func
    def mouse_release_event(self, event):
        """ A method invoked when a mouse release event occurs in the widget.
        
        ** The MouseEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        event : MouseEvent
            The event representing the press operation.
        """
        pass
    
    @d_func
    def draw_background(self, painter, rect):
        """ A method invoked when a background draw is requested.
        
        This method will not normally be implemented, but it can be
        useful for implementing custom backgrounds. This drawing is cached.
        
        ** The DrawBackgroundEnabled feature must be enabled for the widget in
        order for this method to be called. **
        
        Parameters
        ----------
        painter : Painter
            A the toolkit dependent handle drawing.
        rect : Rect
            A rect showing the area of interest.
        """
        pass
    
    # --------------------------------------------------------------------------
    # Graphics Scene API
    # --------------------------------------------------------------------------
    def get_item_at(self, *args, **kwargs):
        """ Return the items at the given position """
        return self.proxy.get_item_at(coerce_point(*args, **kwargs))
    
    def fit_in_view(self, item):
        """ Fit this item into the view """
        self.proxy.fit_in_view(item)
        
    def center_on(self, item):
        """ Center on the given item or point. """
        if not isinstance(item, GraphicsItem):
            item = coerce_point(item)
        self.proxy.center_on(item)
    
    def translate_view(self, x=0, y=0):
        """ Translate the view by the given x and y pixels. """
        return self.proxy.translate_view(x, y)
    
    def scale_view(self, x=1, y=1):
        """ Scale the view by the given x and y factors. """
        return self.proxy.scale_view(x, y)
        
    def rotate_view(self, angle=0):
        """ Roteate the view by the given x and y factors. """
        self.proxy.rotate_view(angle)
        
    def reset_view(self):
        """ Reset all view transformations. """
        self.proxy.reset_view()
        
    def map_from_scene(self, point):
        """ Returns the scene coordinate point mapped to viewport coordinates. 
        """
        return self.proxy.map_from_scene(point)
    
    def map_to_scene(self, point):
        """ Returns the viewport coordinate point mapped to scene coordinates. 
        """
        return self.proxy.map_to_scene(point)
    
    def pixel_density(self):
        """ Returns the size of a pixel in sceen coordinates. 
        """
        return self.proxy.pixel_density()
    
    
class GraphicsItemGroup(GraphicsItem):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsItemGroup)
    
    
class AbstractGraphicsShapeItem(GraphicsItem):
    """ A common base for all path items.
    
    """
    #: Proxy reference
    proxy = Typed(ProxyAbstractGraphicsShapeItem)
    
    #: Set the pen or "line" style.
    pen = d_(Instance(Pen))
    
    #: Set the brush or "fill" style.
    brush = d_(Instance(Brush))
    
    @observe('pen', 'brush')
    def _update_proxy(self, change):
        super(AbstractGraphicsShapeItem, self)._update_proxy(change)
        

class GraphicsRectItem(AbstractGraphicsShapeItem):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsRectItem)
    
    #: Width
    width = d_(Float(10.0, strict=False))
    
    #: Height
    height = d_(Float(10.0, strict=False))
    
    @observe('width', 'height')
    def _update_proxy(self, change):
        super(GraphicsRectItem, self)._update_proxy(change)
        

class GraphicsEllipseItem(AbstractGraphicsShapeItem):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsEllipseItem)
    
    #: Width
    width = d_(Float(10.0, strict=False))
    
    #: Height
    height = d_(Float(10.0, strict=False))
    
    #: Sets the span angle for an ellipse segment to angle.
    #: This is rounded to the nearest 16ths of a degree.
    span_angle = d_(Float(360.0, strict=False))
    
    #: Sets the start angle for an ellipse segment to angle.
    #: This is rounded to the nearest 16ths of a degree.
    start_angle = d_(Float(0.0, strict=False))
    
    @observe('width', 'height', 'span_angle', 'start_angle')
    def _update_proxy(self, change):
        super(GraphicsEllipseItem, self)._update_proxy(change)

        
class GraphicsTextItem(AbstractGraphicsShapeItem):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsTextItem)
    
    #: Text
    text = d_(Unicode())
    
    #: Font
    font = d_(FontMember())
    
    @observe('text', 'font')
    def _update_proxy(self, change):
        super(GraphicsTextItem, self)._update_proxy(change)


class GraphicsLineItem(AbstractGraphicsShapeItem):
    """ Creates a line from the position x,y to the given point """
    #: Proxy reference
    proxy = Typed(ProxyGraphicsLineItem)
    
    #: An x,y or x,y,z point
    point = d_(PointMember())
    
    @observe('point')
    def _update_proxy(self, change):
        super(GraphicsLineItem, self)._update_proxy(change)


class GraphicsPolygonItem(AbstractGraphicsShapeItem):
    """ Creates a line from the position x,y to the given point """
    #: Proxy reference
    proxy = Typed(ProxyGraphicsPolygonItem)
    
    #: A list of (x,y) or (x,y,z) points
    #: TODO: Support np array
    points = d_(List(PointMember()))
    
    @observe('points')
    def _update_proxy(self, change):
        super(GraphicsPolygonItem, self)._update_proxy(change)


class GraphicsPathItem(AbstractGraphicsShapeItem):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsPathItem)
    
    #: Path. For now you must pass a QPainterPath until some "abstract"
    #: path value and format is accepted.
    path = d_(Value())
    
    @observe('path')
    def _update_proxy(self, change):
        super(GraphicsPathItem, self)._update_proxy(change)
    

class GraphicsImageItem(GraphicsItem):
    #: Proxy reference
    proxy = Typed(ProxyGraphicsImageItem)
    
    #: Image
    image = d_(Instance(Image))
    
    @observe('image')
    def _update_proxy(self, change):
        super(GraphicsImageItem, self)._update_proxy(change)
        
        
class GraphicsWidget(GraphicsItem):
    """ Use this to embed a widget within a graphics scene """
    #: Proxy reference
    proxy = Typed(ProxyGraphicsWidget)
    
