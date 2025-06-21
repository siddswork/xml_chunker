"""Logging configuration for XSLT Test Generator."""

import logging
import logging.config
import structlog
from pathlib import Path
from typing import Dict, Any
import os
from datetime import datetime


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    enable_structured_logging: bool = True
) -> None:
    """
    Configure comprehensive logging for the XSLT Test Generator.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_dir: Directory for log files
        enable_structured_logging: Whether to use structured logging
    """
    
    # Create logs directory
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Generate timestamped log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"xslt_test_gen_{timestamp}.log"
        error_log_file = log_path / f"xslt_test_gen_errors_{timestamp}.log"
    
    # Configure standard logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(name)s - %(message)s"
            },
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                }
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "xslt_test_generator": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "xslt_test_generator.agents": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            },
            "xslt_test_generator.tools": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    # Add file handlers if enabled
    if log_to_file:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
        
        logging_config["handlers"]["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed", 
            "filename": str(error_log_file),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
        
        # Add file handlers to all loggers
        for logger_name in logging_config["loggers"]:
            logging_config["loggers"][logger_name]["handlers"].extend(["file", "error_file"])
        
        logging_config["root"]["handlers"].extend(["file", "error_file"])
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Configure structured logging if enabled
    if enable_structured_logging:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def get_structured_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structured logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get a logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    @property
    def struct_logger(self) -> structlog.BoundLogger:
        """Get a structured logger for this class."""
        return get_structured_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_agent_interaction(
    agent_name: str,
    operation: str,
    input_data: Dict[str, Any] = None,
    output_data: Dict[str, Any] = None,
    execution_time: float = None,
    status: str = "success"
) -> None:
    """
    Log agent interactions with structured data.
    
    Args:
        agent_name: Name of the agent
        operation: Operation being performed
        input_data: Input data (sanitized)
        output_data: Output data (sanitized)
        execution_time: Time taken for operation
        status: Status of operation (success, error, warning)
    """
    logger = get_structured_logger("xslt_test_generator.agents")
    
    log_data = {
        "agent": agent_name,
        "operation": operation,
        "status": status,
        "execution_time": execution_time
    }
    
    if input_data:
        log_data["input"] = _sanitize_log_data(input_data)
    
    if output_data:
        log_data["output"] = _sanitize_log_data(output_data)
    
    if status == "success":
        logger.info("Agent operation completed", **log_data)
    elif status == "error":
        logger.error("Agent operation failed", **log_data)
    else:
        logger.warning("Agent operation completed with warnings", **log_data)


def _sanitize_log_data(data: Dict[str, Any], max_length: int = 1000) -> Dict[str, Any]:
    """
    Sanitize log data to prevent logging sensitive information and limit size.
    
    Args:
        data: Data to sanitize
        max_length: Maximum length for string values
        
    Returns:
        Sanitized data
    """
    if not isinstance(data, dict):
        return {"type": type(data).__name__, "length": len(str(data))}
    
    sanitized = {}
    for key, value in data.items():
        # Skip potentially sensitive keys
        if any(sensitive in key.lower() for sensitive in ["password", "token", "key", "secret"]):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, str) and len(value) > max_length:
            sanitized[key] = value[:max_length] + "... [TRUNCATED]"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_log_data(value, max_length)
        else:
            sanitized[key] = value
    
    return sanitized