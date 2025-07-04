"""
AI Prompt Engineering System - Core Package

A structured prompt engineering system with 3-layer hierarchical rules:
- Primitive Rules: Basic building blocks
- Semantic Rules: Context-aware templates
- Task Rules: Specific use-case implementations
"""

from .database import (
    db_manager, setup_database_system,
    primitive_crud, semantic_crud, task_crud,
    relation_crud, version_crud, tag_crud,
    migration_manager, validate_database, generate_sample_data, clear_sample_data,
    get_db_connection
)

__version__ = "1.0.0"
__author__ = "AI Prompt Engineering System"

# Convenience functions for common operations
def setup_database(with_sample_data: bool = False) -> dict:
    """
    Initialize database with schema and optionally add sample data.

    Args:
        with_sample_data: Whether to create sample data for testing

    Returns:
        Dictionary with setup results
    """
    results = {
        'database_initialized': False,
        'migrations_applied': False,
        'sample_data_created': False,
        'validation_passed': False,
        'errors': []
    }

    try:
        # Setup database system
        setup_database_system(with_sample_data=with_sample_data)
        results['database_initialized'] = True

        # Apply migrations if any
        migration_status = migration_manager.get_migration_status()
        if migration_status['pending_count'] > 0:
            migration_manager.migrate_up()
            results['migrations_applied'] = True

        # Create sample data if requested
        if with_sample_data:
            generate_sample_data()
            results['sample_data_created'] = True

        # Validate database
        validation_result = validate_database()
        results['validation_passed'] = validation_result['valid']
        if not validation_result['valid']:
            results['errors'].extend(validation_result['errors'])

    except Exception as e:
        results['errors'].append(str(e))

    return results


def get_system_status() -> dict:
    """
    Get comprehensive system status.

    Returns:
        Dictionary with system status information
    """
    try:
        # Database stats
        db_stats = db_manager.get_database_stats()

        # Migration status
        migration_status = migration_manager.get_migration_status()

        # Validation status
        validation_result = validate_database()

        return {
            'database_stats': db_stats,
            'migration_status': migration_status,
            'validation_passed': validation_result['valid'],
            'version': __version__
        }

    except Exception as e:
        return {
            'error': str(e),
            'version': __version__
        }


# Export key classes and functions
__all__ = [
    # Core classes
    'db_manager',
    'primitive_crud',
    'semantic_crud',
    'task_crud',
    'relation_crud',
    'version_crud',
    'tag_crud',
    'migration_manager',

    # Setup functions
    'setup_database',
    'get_system_status',

    # Data functions
    'generate_sample_data',
    'clear_sample_data',

    # Validation functions
    'validate_database',

    # Utility functions
    'get_db_connection'
]
