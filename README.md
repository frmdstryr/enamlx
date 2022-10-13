# enamlx

Additional Qt Widgets for Enaml, mainly used for the Tree and Table widgets.

Supports 3.5+ Qt5 and Qt6.

## Install

Now on [pypi](https://pypi.org/project/enamlx/).

```bash

pip install enamlx

```

#### Widgets ####

1. TableView
2. TreeView
3. DoubleSpinBox
4. GraphicsView
5. PyQtGraph Plot
6. KeyEvent


#### Examples ####

__TableView__

Table view using enaml syntax. See example for usage.

![table view](https://lh6.googleusercontent.com/FUfzbzZpsMuGymnNdzBeXgONZXJGQreswK05lMP1zRlesxY70Xo14dxYBBOrqb23DCf6yOMeXYqHNxEaNtdc13GNmri6-pQ3-uoq4rcgRvHh3b8J58MVx_xZaifCHz2Hv0Q3CoQ)

1. Text/Icons/Checkboxes
2. Delegate widgets (any widget can be child of a cell)
3. Right click menus per item
4. Tested and working with 1 million+ rows.



__DoubleSpinBox__

SpinBox that works with float values


__PlotItem__

Plot widgets using PyQtGraph


![plot item](https://lh5.googleusercontent.com/pqa4WZnMzaU72pYnqc75AghnJGC8Z6kCELcsHkR3n_VTQzEmCB9di7reqqQbCIpnfAVXSCEXK6y07_DMyQ51XUCUAOe-xczfKsYKCRROPbUlDHcGMNSFaBmZRGxXP9Clya_q34I)


__GraphicsView__

A "canvas" Widget for drawing with Qt's GraphicsView.



# Usage

```python

import enamlx
enamlx.install()

# Then use like any enaml widget
from enamlx.widgets.api import TreeView # etc..

```
