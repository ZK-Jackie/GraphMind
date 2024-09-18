"""
GraphMind Engine module root.

2 types of engines are supported in GraphMind currently:
- `hierarchy` for hierarchy-based knowledge extraction.
- `chunk` for chunk-based knowledge extraction

1 type of engine is under development:
- `cascade` for cascade-based knowledge extraction.
"""

from graphmind.adapter.engine.base import BaseEngine

import graphmind.adapter.engine.support_config as SUPPORT_CONFIG

__all__ = ["BaseEngine",
           "SUPPORT_CONFIG"]
