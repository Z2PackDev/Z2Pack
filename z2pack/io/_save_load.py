"""Defines functions for saving and loading Z2Pack objects."""

from fsc.iohelper import SerializerDispatch

from . import _encoding

__all__ = ['save', 'load']

IO_HANDLER = SerializerDispatch(_encoding)

# pylint: disable=invalid-name
save = IO_HANDLER.save
load = IO_HANDLER.load
