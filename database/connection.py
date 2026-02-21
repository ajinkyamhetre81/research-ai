# database/connection.py

import os
import psycopg2
from typing import Optional, Dict, Any, List
from utils.loggers import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """ PostgreSQL database connection."""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.config = self._get_db_config()
    
    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'research_ai'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.cursor = self.connection.cursor()
            
            logger.info(f"Connected to PostgreSQL: {self.config['database']}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Database connection closed")
        except psycopg2.Error as e:
            logger.error(f"Error closing connection: {e}")
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return results."""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            logger.error(f"Query error: {e}")
            return None
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE query."""
        try:
            if not self.connection or self.connection.closed:
                self.connect()
            
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Update error: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information."""
        if not self.connection or self.connection.closed:
            return {
                "status": "disconnected",
                "database": self.config['database'],
                "host": self.config['host'],
                "port": self.config['port']
            }
        
        try:
            # Test connection with simple query
            self.cursor.execute("SELECT 1 as test;")
            test_result = self.cursor.fetchone()
            
            return {
                "status": "connected",
                "database": self.config['database'],
                "host": self.config['host'],
                "port": self.config['port'],
                "test_query": "passed" if test_result[0] == 1 else "failed"
            }
        except Exception as e:
            return {
                "status": "error",
                "database": self.config['database'],
                "host": self.config['host'],
                "port": self.config['port'],
                "error": str(e)
            }


# Global instance
db = DatabaseConnection()


def get_db():
    """Get database connection."""
    return db
