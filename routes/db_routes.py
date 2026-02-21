# routes/db_routes.py

from fastapi import APIRouter, HTTPException
from database import get_db
from utils.loggers import get_logger, log_operation_start, log_operation_end

router = APIRouter()
logger = get_logger(__name__)


@router.get("/db-status")
async def get_database_status():
    """Get database connection status."""
    log_operation_start(logger, "Database status check")
    
    try:
        db = get_db()
        
        # Test connection
        if db.connect():
            info = db.get_connection_info()
            
            log_operation_end(logger, "Database status check", True, "Connection verified successfully")
            
            return {
                "status": "connected",
                "database": info.get("database"),
                "host": info.get("host"),
                "port": info.get("port"),
                "message": "Database connection is active",
                "timestamp": logger.info("Status checked")
            }
        else:
            log_operation_end(logger, "Database status check", False, "Connection failed")
            
            return {
                "status": "disconnected",
                "message": "Database connection failed",
                "error": "Unable to establish database connection",
                "config": {
                    "host": db.config.get("host"),
                    "port": db.config.get("port"),
                    "database": db.config.get("database")
                }
            }
            
    except Exception as e:
        log_operation_end(logger, "Database status check", False, f"Error: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Database status check failed: {str(e)}"
        )


@router.post("/db-test")
async def test_database_connection():
    """Test database connection with query execution."""
    log_operation_start(logger, "Database connection test")
    
    try:
        db = get_db()
        
        if not db.connect():
            log_operation_end(logger, "Database connection test", False, "Connection failed")
            
            return {
                "success": False,
                "message": "Database connection failed",
                "error": "Unable to establish database connection"
            }
        
        # Test basic query
        test_results = {}
        
        # Test SELECT
        try:
            results = db.execute_query("SELECT version() as db_version;")
            test_results["select_test"] = {
                "success": True,
                "result": results[0] if results else None
            }
        except Exception as e:
            test_results["select_test"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test INSERT
        try:
            insert_success = db.execute_update(
                "CREATE TABLE IF NOT EXISTS connection_test (id SERIAL PRIMARY KEY, test_data TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
            )
            test_results["create_table_test"] = {
                "success": insert_success
            }
        except Exception as e:
            test_results["create_table_test"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test cleanup
        try:
            cleanup_success = db.execute_update("DROP TABLE IF EXISTS connection_test;")
            test_results["cleanup_test"] = {
                "success": cleanup_success
            }
        except Exception as e:
            test_results["cleanup_test"] = {
                "success": False,
                "error": str(e)
            }
        
        # Overall result
        all_tests_passed = all(
            test["success"] for test in test_results.values()
        )
        
        log_operation_end(
            logger, 
            "Database connection test", 
            all_tests_passed, 
            f"Tests passed: {sum(1 for test in test_results.values() if test['success'])}/{len(test_results)}"
        )
        
        db.disconnect()
        
        return {
            "success": all_tests_passed,
            "message": "Database connection test completed",
            "tests": test_results,
            "overall_status": "passed" if all_tests_passed else "failed"
        }
        
    except Exception as e:
        log_operation_end(logger, "Database connection test", False, f"Unexpected error: {str(e)}")
        
        return {
            "success": False,
            "message": "Database connection test failed",
            "error": str(e)
        }
