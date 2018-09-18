# -*- coding: utf-8 -*-
"""
Copyright (c) 2018, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Sept 17, 2018
"""
from enaml.core.parser.base_lexer import BaseEnamlLexer

# Save a reference to the original method
default_make_token_stream = BaseEnamlLexer.make_token_stream
_token_stream_processors = []


def _custom_token_stream(self):
    """ A wrapper for the BaseEnamlLexer's make_token_stream which allows
    the stream to be customized by adding "token_stream_processors".
    
    A token_stream_processor is a generator function which takes the 
    token_stream as it's single input argument and yields each processed token 
    as it's output. Each token will be an instance of `ply.lex.LexToken`.
    
    """
    token_stream = default_make_token_stream(self)
    for processor in _token_stream_processors:
        token_stream = processor(token_stream)
    return token_stream


def add_token_stream_processor(processor):
    """ Add a token stream processor and install the custom token stream
    method if it is not already installed.
    
    """
    install()
    _token_stream_processors.append(processor)


def remote_token_stream_processor(processor):
    """ Removes the given token stream processor and uninstalls the custom 
    token stream if it is no longer needed.
    
    """
    _token_stream_processors.remove(processor)
    if not token_stream_processors:
        uninstall()
    

def install():
    """ Install the custom token stream processor. 
    
    """
    if BaseEnamlLexer.make_token_stream != _custom_token_stream:
        BaseEnamlLexer.make_token_stream = _custom_token_stream


def uninstall():
    """ Install the custom token stream processor. 
    
    """
    if BaseEnamlLexer.make_token_stream == _custom_token_stream:
        BaseEnamlLexer.make_token_stream = default_make_token_stream    
    
    
def convert_enamldef_def_to_func(token_stream):
    """ A token stream processor which processes all enaml declarative functions 
    to allow using `def` instead of `func`. It does this by transforming DEF 
    tokens to NAME within enamldef blocks and then changing the token value to 
    `func`.
    
    Notes
    ------
    Use this at your own risk!  This was a feature intentionally
    dismissed by the author of enaml because declarative func's are not the
    same as python functions.

    """
    in_enamldef = False
    depth = 0
    for tok in token_stream:
        if tok.type == 'ENAMLDEF':
            in_enamldef = True
        elif tok.type == 'INDENT':
            depth += 1
        elif in_enamldef and tok.type == 'DEF':
            # Since functions are not allowed on the RHS we can
            # transform the token type to a NAME so it's picked up by the
            # parser as a decl_funcdef instead of funcdef
            tok.type = 'NAME'
            tok.value = 'func'
        elif tok.type == 'DEDENT':
            depth -= 1
            if depth == 0:
                in_enamldef = False
        yield tok
