"""
Court finder providers module.

This module contains provider implementations for different court booking platforms.
All providers inherit from BaseCourtProvider to ensure consistent interfaces.
"""

from app.courtfinder.base_provider import BaseCourtProvider
from app.courtfinder.playtomic import PlaytomicProvider

# Backward compatibility - keep old name available
PadelMateService = PlaytomicProvider

__all__ = ["BaseCourtProvider", "PlaytomicProvider", "PadelMateService"]
