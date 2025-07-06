"""
Database connection management and configuration for AI Prompt Engineering System.
"""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Generator, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: str = None):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Use absolute path to the correct database location
            db_path = "/home/jyw/Program/tiered-prompts/ai_prompt_system/database/prompt_system.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    def initialize_database(self, schema_path: Optional[str] = None) -> None:
        """
        Initialize database with schema and indexes.

        Args:
            schema_path: Path to SQL schema file. If None, uses the default schema.sql in the same directory.
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.sql"
        else:
            schema_path = Path(schema_path)

        try:
            with self.get_connection() as conn:
                # Read and execute schema
                if schema_path.exists():
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema_sql = f.read()

                    # Execute schema as a script (handles multiple statements)
                    conn.executescript(schema_sql)

                    conn.commit()
                    logger.info(f"Database initialized successfully from {schema_path}")
                else:
                    logger.error(f"Schema file not found: {schema_path}")
                    raise FileNotFoundError(f"Schema file not found: {schema_path}")

            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Get database connection with proper error handling and cleanup.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of query results as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT query and return last row ID.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Last inserted row ID
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def backup_database(self, backup_path: str) -> None:
        """
        Create database backup.

        Args:
            backup_path: Path for backup file
        """
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as source:
            backup_conn = sqlite3.connect(str(backup_file))
            try:
                source.backup(backup_conn)
                logger.info(f"Database backed up to {backup_path}")
            finally:
                backup_conn.close()

    def validate_database(self) -> Dict[str, Any]:
        """
        Validate database integrity and structure.

        Returns:
            Dictionary with validation results
        """
        results = {
            "integrity_check": False,
            "foreign_key_check": False,
            "table_count": 0,
            "index_count": 0,
            "trigger_count": 0,
            "errors": []
        }

        try:
            with self.get_connection() as conn:
                # Check database integrity
                integrity_result = conn.execute("PRAGMA integrity_check").fetchone()
                results["integrity_check"] = integrity_result[0] == "ok"

                # Check foreign key constraints
                fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
                results["foreign_key_check"] = len(fk_violations) == 0
                if fk_violations:
                    results["errors"].extend([dict(row) for row in fk_violations])

                # Count database objects
                tables = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()
                results["table_count"] = tables[0]

                indexes = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'").fetchone()
                results["index_count"] = indexes[0]

                triggers = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'").fetchone()
                results["trigger_count"] = triggers[0]

        except Exception as e:
            results["errors"].append(str(e))
            logger.error(f"Database validation failed: {e}")

        return results

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics and usage information.

        Returns:
            Dictionary with database statistics
        """
        stats = {}

        try:
            with self.get_connection() as conn:
                # Count records in each table
                tables = [
                    "primitive_rules", "semantic_rules", "task_rules",
                    "semantic_primitive_relations", "task_semantic_relations",
                    "rule_versions", "rule_tags"
                ]

                for table in tables:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                    stats[f"{table}_count"] = count[0]

                # Database file size
                stats["database_size_bytes"] = self.db_path.stat().st_size if self.db_path.exists() else 0

                # Last modification time
                if self.db_path.exists():
                    stats["last_modified"] = datetime.fromtimestamp(
                        self.db_path.stat().st_mtime
                    ).isoformat()

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            stats["error"] = str(e)

        return stats


# Global database manager instance
db_manager = DatabaseManager()


def initialize_database():
    """Initialize the database with schema."""
    db_manager.initialize_database()


def get_db_connection():
    """Get database connection context manager."""
    return db_manager.get_connection()


def validate_json_field(value: Optional[str]) -> bool:
    """
    Validate JSON field content.

    Args:
        value: JSON string to validate

    Returns:
        True if valid JSON or None, False otherwise
    """
    if value is None:
        return True

    try:
        json.loads(value)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def format_timestamp(timestamp: Optional[str]) -> Optional[str]:
    """
    Format timestamp for consistent display.

    Args:
        timestamp: ISO timestamp string

    Returns:
        Formatted timestamp or None
    """
    if not timestamp:
        return None

    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return timestamp
