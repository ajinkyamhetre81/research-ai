# database/__init__.py

from .connection import get_db, DatabaseConnection

__all__ = ['get_db', 'DatabaseConnection']
