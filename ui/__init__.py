# ui/__init__.py
"""
SecureDiary UI Package
Encrypted personal journal with modern dark theme
"""

from .diary_ui import DiaryWindow
from .entry_ui import AddEntryWindow, ViewEntryWindow

__all__ = ['DiaryWindow', 'AddEntryWindow', 'ViewEntryWindow']
