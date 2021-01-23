"""
Middleware to Dispatch to multiple ASGI applications, extracted from hypercorn.
"""

from __future__ import generator_stop

from ._core import DispatcherMiddleware

__all__ = ["DispatcherMiddleware"]

__version__ = "0.0.0a3.dev0"
