"""
Validation Package

Contains the ValidationGate which enforces quality constraints
on all chapter outputs before they can be rendered.
"""

from backend.validation.gate import ValidationGate

__all__ = ["ValidationGate"]
