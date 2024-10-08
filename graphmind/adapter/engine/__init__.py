"""
GraphMind Engine module root.

2 types of engines are supported in GraphMind currently:
- `hierarchy` for hierarchy-based knowledge extraction.
- `chunk` for chunk-based knowledge extraction

1 type of engine is under development:
- `cascade` for cascade-based knowledge extraction.
"""

from graphmind.adapter.engine.base import BaseEngine

__all__ = ["BaseEngine"]
