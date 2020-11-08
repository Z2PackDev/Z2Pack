#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper tools for adding tags to a log and managing filter."""

import copy
import logging
from contextlib import contextmanager


class TagAdapter(logging.LoggerAdapter):
    r"""
    LoggerAdapter to facilitate adding tags to a log. The LogRecord instances will have a ``tags`` attribute. The logging function can take the ``tags`` keyword.

    :param logger:  The logger which is to be adapted.

    :param default_tags:    Tags which are added to all LogRecords.
    """
    def __init__(self, logger, default_tags=()):
        super().__init__(logger, extra={'tags': set(default_tags)})

    def process(self, msg, kwargs=None):
        tags = copy.deepcopy(self.extra['tags'])
        # check for "manual" tags
        tags.update(kwargs.pop('tags', []))  # don't pass on tags kwargs
        # "extra" kwarg must exist, add tags
        kwargs.setdefault('extra', dict())['tags'] = tags
        return msg, kwargs


class TagFilter:
    """Filter a message if it has a tag which is in ``filter_tags``."""
    def __init__(self, filter_tags):
        self.filter_tags = filter_tags

    def filter(self, record):
        try:
            return not any(tag in self.filter_tags for tag in record.tags)
        except AttributeError:
            return True


@contextmanager
def filter_manager(logger, filter_):
    """Adds a filter to a specific logger, and removes it upon exiting."""
    logger.addFilter(filter_)
    try:
        yield
    except Exception as exc:
        raise exc
    finally:
        logger.removeFilter(filter_)
