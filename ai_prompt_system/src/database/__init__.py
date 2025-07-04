"""
Database module for AI Prompt Engineering System.

This module provides all database-related functionality including:
- Connection management
- CRUD operations for all rule types
- Database migrations
- Data validation
- Sample data generation
"""

from .connection import DatabaseManager, get_db_connection, initialize_database
from .crud import (
    PrimitiveRuleCRUD, SemanticRuleCRUD, TaskRuleCRUD,
    RelationCRUD, VersionCRUD, TagCRUD,
    primitive_crud, semantic_crud, task_crud, relation_crud, version_crud, tag_crud
)
from .validation import (
    DatabaseValidator, validate_database
)
from .migrations import MigrationManager, migration_manager
from .seed_data import SeedDataManager, generate_sample_data, clear_sample_data

# Database manager instance
db_manager = DatabaseManager()

# Main setup function
def setup_database_system(with_sample_data: bool = False) -> None:
    """
    Setup the complete database system.

    Args:
        with_sample_data: Whether to generate sample data
    """
    # Initialize database
    initialize_database()

    if with_sample_data:
        generate_sample_data()

__all__ = [
    # Core classes
    'DatabaseManager', 'db_manager',
    'PrimitiveRuleCRUD', 'SemanticRuleCRUD', 'TaskRuleCRUD',
    'RelationCRUD', 'VersionCRUD', 'TagCRUD',
    'DatabaseValidator',
    'MigrationManager', 'SeedDataManager',

    # Instances
    'primitive_crud', 'semantic_crud', 'task_crud',
    'relation_crud', 'version_crud', 'tag_crud',
    'migration_manager',

    # Functions
    'get_db_connection', 'initialize_database', 'setup_database_system',
    'validate_database', 'generate_sample_data', 'clear_sample_data'
]
