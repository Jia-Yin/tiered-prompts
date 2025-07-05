"""
Database migration system for AI Prompt Engineering System.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .connection import db_manager

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration."""

    def __init__(self, version: str, description: str, up_sql: str, down_sql: str = None):
        self.version = version
        self.description = description
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.timestamp = datetime.now()

    def __str__(self):
        return f"Migration {self.version}: {self.description}"


class MigrationManager:
    """Manages database migrations."""

    def __init__(self, migrations_dir: str = "database/migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        self._migration_table_created = False

    def _ensure_migration_table(self):
        """Create migrations tracking table if it doesn't exist."""
        if self._migration_table_created:
            return

        create_table_sql = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        try:
            db_manager.execute_update(create_table_sql)
            self._migration_table_created = True
            logger.info("Migration tracking table ensured")
        except Exception as e:
            logger.error(f"Failed to create migration table: {e}")
            # Don't raise here to allow system to work without migrations

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        self._ensure_migration_table()
        query = "SELECT version FROM migrations ORDER BY version"
        try:
            results = db_manager.execute_query(query)
            return [row['version'] for row in results]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []

    def is_migration_applied(self, version: str) -> bool:
        """Check if a migration version has been applied."""
        applied = self.get_applied_migrations()
        return version in applied

    def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration."""
        self._ensure_migration_table()
        if self.is_migration_applied(migration.version):
            logger.info(f"Migration {migration.version} already applied")
            return True

        try:
            with db_manager.get_connection() as conn:
                # Execute migration SQL
                statements = [stmt.strip() for stmt in migration.up_sql.split(';') if stmt.strip()]
                for statement in statements:
                    conn.execute(statement)

                # Record migration as applied
                conn.execute(
                    "INSERT INTO migrations (version, description) VALUES (?, ?)",
                    (migration.version, migration.description)
                )

                conn.commit()
                logger.info(f"Applied migration {migration.version}: {migration.description}")
                return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False

    def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration."""
        if not self.is_migration_applied(migration.version):
            logger.info(f"Migration {migration.version} not applied, cannot rollback")
            return True

        if not migration.down_sql:
            logger.error(f"Migration {migration.version} has no rollback SQL")
            return False

        try:
            with db_manager.get_connection() as conn:
                # Execute rollback SQL
                statements = [stmt.strip() for stmt in migration.down_sql.split(';') if stmt.strip()]
                for statement in statements:
                    conn.execute(statement)

                # Remove migration record
                conn.execute("DELETE FROM migrations WHERE version = ?", (migration.version,))

                conn.commit()
                logger.info(f"Rolled back migration {migration.version}")
                return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False

    def create_migration_file(self, version: str, description: str, up_sql: str, down_sql: str = None) -> Path:
        """Create a new migration file."""
        filename = f"{version}_{description.lower().replace(' ', '_')}.sql"
        filepath = self.migrations_dir / filename

        content = f"""-- Migration: {version}
-- Description: {description}
-- Created: {datetime.now().isoformat()}

-- UP Migration
{up_sql}

-- DOWN Migration (Rollback)
{down_sql or '-- No rollback SQL provided'}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created migration file: {filepath}")
        return filepath

    def load_migration_from_file(self, filepath: Path) -> Migration:
        """Load migration from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse migration file
        lines = content.split('\n')
        version = None
        description = None
        up_sql = []
        down_sql = []
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('-- Migration:'):
                version = line.split(':', 1)[1].strip()
            elif line.startswith('-- Description:'):
                description = line.split(':', 1)[1].strip()
            elif line == '-- UP Migration':
                current_section = 'up'
            elif line == '-- DOWN Migration (Rollback)':
                current_section = 'down'
            elif line and not line.startswith('--'):
                if current_section == 'up':
                    up_sql.append(line)
                elif current_section == 'down':
                    down_sql.append(line)

        if not version or not description:
            raise ValueError(f"Invalid migration file format: {filepath}")

        return Migration(
            version=version,
            description=description,
            up_sql='\n'.join(up_sql),
            down_sql='\n'.join(down_sql) if down_sql else None
        )

    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        pending = []

        # Load migrations from files
        for filepath in sorted(self.migrations_dir.glob("*.sql")):
            try:
                migration = self.load_migration_from_file(filepath)
                if migration.version not in applied:
                    pending.append(migration)
            except Exception as e:
                logger.error(f"Failed to load migration {filepath}: {e}")

        return sorted(pending, key=lambda m: m.version)

    def migrate_up(self) -> bool:
        """Apply all pending migrations."""
        pending = self.get_pending_migrations()

        if not pending:
            logger.info("No pending migrations")
            return True

        success = True
        for migration in pending:
            if not self.apply_migration(migration):
                success = False
                break

        return success

    def migrate_down(self, target_version: str = None) -> bool:
        """Rollback migrations to target version."""
        applied = self.get_applied_migrations()

        if target_version:
            # Rollback to specific version
            to_rollback = [v for v in applied if v > target_version]
        else:
            # Rollback one migration
            to_rollback = applied[-1:] if applied else []

        success = True
        for version in reversed(to_rollback):
            # Load migration file to get rollback SQL
            migration_files = list(self.migrations_dir.glob(f"{version}_*.sql"))
            if not migration_files:
                logger.error(f"Migration file not found for version {version}")
                success = False
                break

            try:
                migration = self.load_migration_from_file(migration_files[0])
                if not self.rollback_migration(migration):
                    success = False
                    break
            except Exception as e:
                logger.error(f"Failed to rollback migration {version}: {e}")
                success = False
                break

        return success

    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status information."""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()

        return {
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied_migrations": applied,
            "pending_migrations": [f"{m.version}: {m.description}" for m in pending],
            "current_version": applied[-1] if applied else None
        }


# For backward compatibility - create alias
DatabaseMigrator = MigrationManager

# Global migration manager instance
migration_manager = MigrationManager()


# Predefined migrations for common operations
def create_initial_migrations():
    """Create initial migration files for the schema."""

    # Migration 001: Initial schema
    schema_path = Path("database/schema.sql")
    if schema_path.exists():
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        migration_manager.create_migration_file(
            version="001",
            description="Initial database schema",
            up_sql=schema_sql,
            down_sql="""
DROP TABLE IF EXISTS rule_tags;
DROP TABLE IF EXISTS rule_versions;
DROP TABLE IF EXISTS task_semantic_relations;
DROP TABLE IF EXISTS semantic_primitive_relations;
DROP TABLE IF EXISTS task_rules;
DROP TABLE IF EXISTS semantic_rules;
DROP TABLE IF EXISTS primitive_rules;
"""
        )

    # Migration 002: Add performance indexes (if not in initial schema)
    migration_manager.create_migration_file(
        version="002",
        description="Add additional performance indexes",
        up_sql="""
-- Additional indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_primitive_rules_updated_at ON primitive_rules(updated_at);
CREATE INDEX IF NOT EXISTS idx_semantic_rules_updated_at ON semantic_rules(updated_at);
CREATE INDEX IF NOT EXISTS idx_task_rules_updated_at ON task_rules(updated_at);

-- Indexes for relationship weights
CREATE INDEX IF NOT EXISTS idx_semantic_primitive_weight ON semantic_primitive_relations(weight);
CREATE INDEX IF NOT EXISTS idx_task_semantic_weight ON task_semantic_relations(weight);
""",
        down_sql="""
DROP INDEX IF EXISTS idx_primitive_rules_updated_at;
DROP INDEX IF EXISTS idx_semantic_rules_updated_at;
DROP INDEX IF EXISTS idx_task_rules_updated_at;
DROP INDEX IF EXISTS idx_semantic_primitive_weight;
DROP INDEX IF EXISTS idx_task_semantic_weight;
"""
    )


if __name__ == "__main__":
    # Create initial migrations when run directly
    create_initial_migrations()
