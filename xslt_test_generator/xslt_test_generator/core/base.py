"""Base classes and utilities for the XSLT Test Generator."""

from abc import ABC
from typing import Any
import logging


class LoggerMixin:
    """Mixin class to provide logging functionality to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger


class BaseAnalyzer(LoggerMixin, ABC):
    """Base class for all analyzers."""
    
    def __init__(self):
        super().__init__()
        self.logger.debug(f"Initialized {self.__class__.__name__}")


class BaseProcessor(LoggerMixin, ABC):
    """Base class for all processors."""
    
    def __init__(self):
        super().__init__()
        self.logger.debug(f"Initialized {self.__class__.__name__}")