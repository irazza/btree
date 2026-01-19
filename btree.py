"""Compatibility shim for importing SortedDict from the C extension."""

from btreedict import SortedDict

__all__ = ["SortedDict"]
