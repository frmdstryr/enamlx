"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Sep 26, 2016
"""
import signal

from atom.api import Instance, ForwardInstance, ForwardTyped

from ..widgets.console import ProxyConsole

from qtpy import QtCore, QT_API
from enaml.qt.qt_control import QtControl


def console_factory():
    try:
        from qtconsole.rich_jupyter_widget import RichJupyterWidget as RichIPythonWidget
    except ImportError:
        from IPython.qt.console.rich_ipython_widget import RichIPythonWidget

    # TODO: Support IPython < 3
    return RichIPythonWidget


def kernel_factory():
    try:
        from qtconsole.inprocess import QtInProcessKernelManager
    except ImportError:
        from IPython.qt.console.inprocess import QtInProcessKernelManager
    return QtInProcessKernelManager


class QtConsole(QtControl, ProxyConsole):
    #: Viewer widget
    widget = ForwardTyped(console_factory)

    #: Kernel
    kernel = ForwardInstance(kernel_factory)

    #: So it can exit
    _sigint_timer = Instance(QtCore.QTimer)

    def create_widget(self):
        d = self.declaration
        WidgetClass = console_factory()
        self.widget = WidgetClass(
            parent=self.parent_widget(),
            gui_completion=d.completion,
            display_banner=d.display_banner,
        )

    def init_widget(self):
        d = self.declaration
        self.init_kernel()
        self.init_signal()
        self.set_console_size(d.console_size)

        if d.font_family:
            self.set_font_family(d.font_family)
        if d.font_size:
            self.set_font_size(d.font_size)
        if d.buffer_size:
            self.set_buffer_size(d.buffer_size)
        if d.scope:
            self.set_scope(d.scope)

    def init_kernel(self):
        d = self.declaration
        KernelManager = kernel_factory()
        kernel_manager = KernelManager()
        kernel_manager.start_kernel(show_banner=False)
        kernel = kernel_manager.kernel
        kernel.gui = "qt4"
        self.kernel = kernel
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        self.widget.kernel_manager = kernel_manager
        self.widget.kernel_client = kernel_client

    def init_signal(self):
        """allow clean shutdown on sigint"""
        signal.signal(signal.SIGINT, lambda sig, frame: self.exit(-2))
        # need a timer, so that QApplication doesn't block until a real
        # Qt event fires (can require mouse movement)
        # timer trick from http://stackoverflow.com/q/4938723/938949
        timer = QtCore.QTimer()
        # Let the interpreter run each 200 ms:
        timer.timeout.connect(lambda: None)
        timer.start(200)
        # hold onto ref, so the timer doesn't get cleaned up
        self._sigint_timer = timer

    def set_font_size(self, size):
        self.widget.font_size = size

    def set_font_family(self, family):
        self.widget.font_family = family

    def set_console_size(self, size):
        self.widget.width = size.width
        self.widget.height = size.height

    def set_buffer_size(self, size):
        self.widget.buffer_size = size

    def set_scope(self, state):
        self.kernel.shell.push(state)

    def set_display_banner(self, enabled):
        self.widget.display_banner = enabled

    def set_completion(self, mode):
        self.widget.gui_completion = mode

    def set_execute(self, *args, **kwargs):
        self.kernel.shell.execute(*args, **kwargs)
