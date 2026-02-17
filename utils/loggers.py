import logging
import os
from pathlib import Path
from datetime import datetime


def setup_detailed_logging():
    """
    Set up simple logging with detailed information for beginners.
    Includes timestamps, file names, line numbers, and more context.
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Detailed format with all useful information
    detailed_format = (
        '%(asctime)s | '
        '%(levelname)-8s | '
        '%(filename)s:%(lineno)d | '
        '%(funcName)s() | '
        '%(message)s'
    )
    
    # Set up basic configuration with detailed format
    logging.basicConfig(
        level=logging.INFO,  # Show INFO and above messages
        format=detailed_format,
        datefmt='%Y-%m-%d %H:%M:%S',  # Detailed timestamp format
        handlers=[
            # Print to console with detailed info
            logging.StreamHandler(),
            # Save to file with detailed info
            logging.FileHandler('logs/app.log', encoding='utf-8')
        ]
    )


def get_logger(name):
    """
    Get a logger for your module.
    
    Args:
        name: Usually use __name__ when calling this function
    
    Returns:
        A logger you can use to print messages with detailed information
    """
    return logging.getLogger(name)


def log_with_context(logger, message, level="INFO", extra_context=None):
    """
    Log a message with additional context information.
    
    Args:
        logger: The logger instance
        message: Your message
        level: INFO, WARNING, ERROR, CRITICAL, DEBUG
        extra_context: Dictionary with extra information
    """
    if extra_context:
        context_str = " | ".join([f"{k}: {v}" for k, v in extra_context.items()])
        full_message = f"{message} | {context_str}"
    else:
        full_message = message
    
    if level.upper() == "DEBUG":
        logger.debug(full_message)
    elif level.upper() == "INFO":
        logger.info(full_message)
    elif level.upper() == "WARNING":
        logger.warning(full_message)
    elif level.upper() == "ERROR":
        logger.error(full_message)
    elif level.upper() == "CRITICAL":
        logger.critical(full_message)
    else:
        logger.info(full_message)


def log_operation_start(logger, operation_name, details=None):
    """Log the start of an operation."""
    message = f" STARTING: {operation_name}"
    if details:
        message += f" | {details}"
    logger.info(message)


def log_operation_end(logger, operation_name, success=True, details=None):
    """Log the end of an operation."""
    status = " COMPLETED" if success else " FAILED"
    message = f"{status}: {operation_name}"
    if details:
        message += f" | {details}"
    logger.info(message)


def log_user_action(logger, user_id, action, details=None):
    """Log user actions with context."""
    message = f" USER {user_id}: {action}"
    if details:
        message += f" | {details}"
    logger.info(message)


# Set up detailed logging when this file is imported
setup_detailed_logging()