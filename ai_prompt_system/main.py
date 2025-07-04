#!/usr/bin/env python3
"""
AI Prompt Engineering System - Command Line Interface

Main CLI for managing the prompt engineering system database.
"""

import click
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src import (
    setup_database, get_system_status, validate_database,
    primitive_crud, semantic_crud, task_crud, relation_crud,
    tag_crud, generate_sample_data, clear_sample_data,
    migration_manager, db_manager
)


@click.group()
@click.option('--db-path', default='database/prompt_system.db', help='Database file path')
@click.pass_context
def cli(ctx, db_path):
    """AI Prompt Engineering System CLI."""
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path

    # Set database path
    db_manager.db_path = Path(db_path)


@cli.command()
@click.option('--with-sample-data', is_flag=True, help='Include sample data')
@click.pass_context
def init(ctx, with_sample_data):
    """Initialize the database."""
    click.echo("Initializing AI Prompt Engineering System database...")

    try:
        result = setup_database(with_sample_data=with_sample_data)

        if result['database_initialized']:
            click.echo("✓ Database initialized successfully")

        if result['migrations_applied']:
            click.echo("✓ Migrations applied")

        if result['sample_data_created']:
            click.echo("✓ Sample data created")

        if result['validation_passed']:
            click.echo("✓ Database validation passed")
        else:
            click.echo("⚠ Database validation failed")
            for error in result['errors']:
                click.echo(f"  Error: {error}")

        if result['errors']:
            click.echo(f"\n{len(result['errors'])} errors occurred during initialization")
            sys.exit(1)
        else:
            click.echo("\nDatabase initialization completed successfully!")

    except Exception as e:
        click.echo(f"Failed to initialize database: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status."""
    try:
        status_info = get_system_status()

        click.echo("AI Prompt Engineering System Status")
        click.echo("=" * 40)

        if 'error' in status_info:
            click.echo(f"Error: {status_info['error']}")
            return

        # Database stats
        db_stats = status_info['database_stats']
        click.echo(f"Database file: {ctx.obj['db_path']}")

        if 'database_size_bytes' in db_stats:
            size_mb = db_stats['database_size_bytes'] / (1024 * 1024)
            click.echo(f"Database size: {size_mb:.2f} MB")

        click.echo("\nRule counts:")
        for key, value in db_stats.items():
            if key.endswith('_count'):
                table_name = key.replace('_count', '').replace('_', ' ').title()
                click.echo(f"  {table_name}: {value}")

        # Migration status
        migration_status = status_info['migration_status']
        click.echo(f"\nMigrations:")
        click.echo(f"  Applied: {migration_status['applied_count']}")
        click.echo(f"  Pending: {migration_status['pending_count']}")

        if migration_status['current_version']:
            click.echo(f"  Current version: {migration_status['current_version']}")

        # Validation status
        validation_passed = status_info['validation_passed']
        status_icon = "✓" if validation_passed else "✗"
        click.echo(f"\nValidation: {status_icon} {'Passed' if validation_passed else 'Failed'}")

        click.echo(f"\nSystem version: {status_info['version']}")

    except Exception as e:
        click.echo(f"Failed to get system status: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate database integrity."""
    click.echo("Running database validation...")

    try:
        results = validate_database()

        if results['valid']:
            click.echo("✓ Database validation passed")
        else:
            click.echo("✗ Database validation failed")

            if results['errors']:
                click.echo(f"\nErrors ({len(results['errors'])}):")
                for error in results['errors']:
                    click.echo(f"  - {error}")

            if results['warnings']:
                click.echo(f"\nWarnings ({len(results['warnings'])}):")
                for warning in results['warnings']:
                    click.echo(f"  - {warning}")

        # Show individual check results
        click.echo(f"\nValidation checks ({len(results['checks'])}):")
        for check_name, check_result in results['checks'].items():
            status = "PASS" if check_result.get('valid', True) else "FAIL"
            click.echo(f"  {check_name}: {status}")

            if not check_result.get('valid', True) and 'count' in check_result:
                click.echo(f"    Issues found: {check_result['count']}")

    except Exception as e:
        click.echo(f"Validation failed: {e}")
        sys.exit(1)


@cli.group()
def rules():
    """Manage rules."""
    pass


@rules.command('list')
@click.option('--type', 'rule_type', type=click.Choice(['primitive', 'semantic', 'task']), help='Rule type to list')
@click.option('--limit', type=int, help='Limit number of results')
def list_rules(rule_type, limit):
    """List rules."""
    try:
        if rule_type == 'primitive' or rule_type is None:
            click.echo("Primitive Rules:")
            rules_list = primitive_crud.get_all(limit=limit)
            for rule in rules_list:
                click.echo(f"  {rule['id']}: {rule['name']} ({rule['category'] or 'No category'})")

        if rule_type == 'semantic' or rule_type is None:
            click.echo("\nSemantic Rules:")
            rules_list = semantic_crud.get_all(limit=limit)
            for rule in rules_list:
                click.echo(f"  {rule['id']}: {rule['name']} ({rule['category'] or 'No category'})")

        if rule_type == 'task' or rule_type is None:
            click.echo("\nTask Rules:")
            rules_list = task_crud.get_all(limit=limit)
            for rule in rules_list:
                click.echo(f"  {rule['id']}: {rule['name']} ({rule['domain'] or 'No domain'})")

    except Exception as e:
        click.echo(f"Failed to list rules: {e}")
        sys.exit(1)


@rules.command('show')
@click.argument('rule_type', type=click.Choice(['primitive', 'semantic', 'task']))
@click.argument('rule_id', type=int)
def show_rule(rule_type, rule_id):
    """Show detailed rule information."""
    try:
        if rule_type == 'primitive':
            rule = primitive_crud.get_by_id(rule_id)
        elif rule_type == 'semantic':
            rule = semantic_crud.get_by_id(rule_id)
        else:
            rule = task_crud.get_by_id(rule_id)

        if not rule:
            click.echo(f"Rule not found: {rule_type} #{rule_id}")
            return

        click.echo(f"{rule_type.title()} Rule #{rule['id']}")
        click.echo("=" * 40)
        click.echo(f"Name: {rule['name']}")

        if rule.get('description'):
            click.echo(f"Description: {rule['description']}")

        if rule.get('category'):
            click.echo(f"Category: {rule['category']}")

        if rule.get('language'):
            click.echo(f"Language: {rule['language']}")

        if rule.get('framework'):
            click.echo(f"Framework: {rule['framework']}")

        if rule.get('domain'):
            click.echo(f"Domain: {rule['domain']}")

        # Show content
        content_field = {
            'primitive': 'content',
            'semantic': 'content_template',
            'task': 'prompt_template'
        }[rule_type]

        click.echo(f"\n{content_field.replace('_', ' ').title()}:")
        click.echo("-" * 20)
        click.echo(rule[content_field])

        # Show tags
        tags = tag_crud.get_tags_for_rule(rule_type, rule_id)
        if tags:
            click.echo(f"\nTags: {', '.join(tags)}")

        click.echo(f"\nCreated: {rule['created_at']}")
        click.echo(f"Updated: {rule['updated_at']}")

    except Exception as e:
        click.echo(f"Failed to show rule: {e}")
        sys.exit(1)


@cli.group()
def data():
    """Manage sample data."""
    pass


@data.command('create')
def create_data():
    """Create sample data."""
    click.echo("Creating sample data...")

    try:
        results = generate_sample_data()

        click.echo("Sample data created successfully!")
        for rule_type, rules in results.items():
            click.echo(f"  {rule_type}: {len(rules)} rules created")

    except Exception as e:
        click.echo(f"Failed to create sample data: {e}")
        sys.exit(1)


@data.command('clear')
@click.confirmation_option(prompt='Are you sure you want to clear all data?')
def clear_data():
    """Clear all data from database."""
    click.echo("Clearing all data...")

    try:
        clear_sample_data()
        click.echo("All data cleared successfully!")

    except Exception as e:
        click.echo(f"Failed to clear data: {e}")
        sys.exit(1)


@cli.group()
def migrate():
    """Database migration commands."""
    pass


@migrate.command('status')
def migration_status():
    """Show migration status."""
    try:
        status = migration_manager.get_migration_status()

        click.echo("Migration Status")
        click.echo("=" * 20)
        click.echo(f"Applied migrations: {status['applied_count']}")
        click.echo(f"Pending migrations: {status['pending_count']}")

        if status['current_version']:
            click.echo(f"Current version: {status['current_version']}")

        if status['pending_migrations']:
            click.echo("\nPending migrations:")
            for migration in status['pending_migrations']:
                click.echo(f"  - {migration}")

    except Exception as e:
        click.echo(f"Failed to get migration status: {e}")
        sys.exit(1)


@migrate.command('up')
def migrate_up():
    """Apply pending migrations."""
    click.echo("Applying pending migrations...")

    try:
        success = migration_manager.migrate_up()

        if success:
            click.echo("✓ All migrations applied successfully")
        else:
            click.echo("✗ Migration failed")
            sys.exit(1)

    except Exception as e:
        click.echo(f"Migration failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def test(ctx):
    """Run basic system tests."""
    click.echo("Running basic system tests...")

    try:
        # Test database connection
        click.echo("Testing database connection...")
        with db_manager.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            if result[0] == 1:
                click.echo("✓ Database connection OK")

        # Test CRUD operations
        click.echo("Testing CRUD operations...")

        # Create test rule
        rule_id = primitive_crud.create_primitive_rule(
            name=f"test_rule_{click.get_current_context().info_name}",
            content="Test content"
        )

        # Read test rule
        rule = primitive_crud.get_by_id(rule_id)
        assert rule is not None

        # Update test rule
        primitive_crud.update(rule_id, description="Updated description")

        # Delete test rule
        primitive_crud.delete(rule_id)

        click.echo("✓ CRUD operations OK")

        # Test validation
        click.echo("Testing validation...")
        validation_result = validate_database()
        if validation_result['valid']:
            click.echo("✓ Validation OK")
        else:
            click.echo("⚠ Validation issues found")

        click.echo("\nAll tests completed!")

    except Exception as e:
        click.echo(f"Test failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
