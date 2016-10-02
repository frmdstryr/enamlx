'''
Created on Sep 26, 2016

@author: 

'''
import signal 

from atom.api import Instance, ForwardTyped

from ..widgets.console import ProxyConsole

from enaml.qt import QtCore
from enaml.qt.qt_control import QtControl

def console_factory():
    try:
        from qtconsole.rich_jupyter_widget import RichJupyterWidget as ConsoleWidget
    except ImportError:
        from IPython.qt.console.rich_ipython_widget import RichIPythonWidget as ConsoleWidget
    
    # TODO: Support IPython < 3
    return ConsoleWidget

def kernel_factory():
    try:
        from qtconsole.inprocess import QtInProcessKernelManager
    except ImportError:
        from IPython.qt.console.inprocess import QtInProcessKernelManager
    return QtInProcessKernelManager


class QtConsole(QtControl,ProxyConsole):
    #: Viewer widget
    widget = ForwardTyped(console_factory)
    
    _sigint_timer = Instance(QtCore.QTimer)
    
    def create_widget(self):
        WidgetClass = console_factory()
        self.widget = WidgetClass(self.parent_widget())
        
    def init_widget(self):
        d = self.declaration
        
        self.init_kernel()
        self.init_signal()
        
    def init_kernel(self):
        d = self.declaration
        KernelManager = kernel_factory()
        kernel_manager = KernelManager()
        kernel_manager.start_kernel(show_banner=False)
        kernel = kernel_manager.kernel
        kernel.gui = d.gui
        
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


        
        
        