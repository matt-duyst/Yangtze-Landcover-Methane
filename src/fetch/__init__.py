"""Acquisition modules, one per source.

Each exposes the same shape: describe what it would fetch, fetch it, and
verify what it fetched against a checksum the publisher supplies. Nothing
here writes a file it has not verified.
"""
