#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines helpers to asynchronously perform a function on data which is added to a queue.
"""

import time
from threading import Thread


class Sentinel:
    """Sentinel object to show that this is the last object to go into the queue. This triggers the termination of the asynchronous task."""

    def __init__(self, obj):
        self.obj = obj


class AsyncHandler:
    """Context manager to handle asynchronous operations on some queue of 1 object. The asynchronous handler works on the latest object sent to it."""

    def __init__(self, handler):
        self.handler = handler
        if self.handler is not None:
            self._empty = object()
            self.write_obj = self._empty
            self.thread = None

    def __enter__(self):
        """Create a thread that will perform the asynchronous task."""
        if self.handler is not None:

            def consume():
                """Consume elements in the queue, stopping if the Sentinel is encounetered."""
                tmp1 = self._empty
                while True:
                    tmp2 = self.write_obj
                    if tmp2 is tmp1:
                        time.sleep(0.5)
                        continue
                    if isinstance(tmp2, Sentinel):
                        if tmp2.obj is not tmp1:
                            self.handler(tmp2.obj)
                        return
                    tmp1 = tmp2
                    self.handler(tmp1)

            # use concurrent.futures if you want to catch exceptions
            # right now we don't catch them at all -- it might be preferable
            # to catch them, but only if the can be caught exactly when
            # they happen (i.e., not after the whole calculation has finished).
            self.thread = Thread(target=consume)
            self.thread.start()
        return self

    def send(self, obj):
        if self.handler is not None:
            self.write_obj = obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handler is not None:
            self.write_obj = Sentinel(self.write_obj)
            self.thread.join()
