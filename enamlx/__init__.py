def install(allow_def=False):
    """Install the toolkit factory widgets for the widgets provided
    by this library.

    """
    from enamlx.qt import qt_factories

    if allow_def:
        allow_def_funcs()


def allow_def_funcs():
    """Installs a patch to the parser so python's def keyword can be
    used instead of enaml's func keyword.

    Notes
    ------
    Use this at your own risk!  This was a feature intentionally
    dismissed by the author of enaml because declarative func's are not the
    same as python functions.

    """
    from enamlx.core import middleware

    middleware.add_token_stream_processor(middleware.convert_enamldef_def_to_func)
