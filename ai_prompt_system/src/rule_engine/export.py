"""
Export/Import/Backup utilities for rules.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import zipfile
import tempfile
import shutil

logger = logging.getLogger(__name__)


class RuleExporter:
    def __init__(self, db):
        self.db = db

    def export_rules(self, filepath: str, rule_types: List[str] = None, format: str = 'json') -> Dict[str, Any]:
        """
        Export rules to file.

        Args:
            filepath: Path to output file
            rule_types: List of rule types to export ('primitive', 'semantic', 'task')
            format: Export format ('json', 'yaml', 'sql')

        Returns:
            Export statistics
        """
        if rule_types is None:
            rule_types = ['primitive', 'semantic', 'task']

        try:
            # Export based on format
            if format.lower() == 'json':
                return self._export_json(filepath, rule_types)
            elif format.lower() == 'yaml':
                return self._export_yaml(filepath, rule_types)
            elif format.lower() == 'sql':
                return self._export_sql(filepath, rule_types)
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def import_rules(self, filepath: str, merge_strategy: str = 'skip_existing') -> Dict[str, Any]:
        """
        Import rules from file.

        Args:
            filepath: Path to input file
            merge_strategy: How to handle existing rules ('skip_existing', 'overwrite', 'create_new')

        Returns:
            Import statistics
        """
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                raise FileNotFoundError(f"Import file not found: {filepath}")

            # Determine format from extension
            extension = file_path.suffix.lower()
            if extension == '.json':
                return self._import_json(filepath, merge_strategy)
            elif extension in ['.yaml', '.yml']:
                return self._import_yaml(filepath, merge_strategy)
            elif extension == '.sql':
                return self._import_sql(filepath, merge_strategy)
            else:
                raise ValueError(f"Unsupported import format: {extension}")

        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise

    def backup_database(self, backup_path: str) -> Dict[str, Any]:
        """
        Create a complete backup of the database.

        Args:
            backup_path: Path to backup file

        Returns:
            Backup statistics
        """
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a ZIP archive with database and metadata
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database file
                with self.db.get_connection() as conn:
                    # Create temporary database dump
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
                        for line in conn.iterdump():
                            tmp.write(line + '\n')
                        tmp_path = tmp.name

                zipf.write(tmp_path, 'database_dump.sql')

                # Add metadata
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'version': '1.0',
                    'statistics': self._get_database_stats()
                }
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))

                # Add rules as JSON for easy reading
                rules_data = self._export_all_rules()
                zipf.writestr('rules.json', json.dumps(rules_data, indent=2))

                # Clean up temp file
                Path(tmp_path).unlink()

            return {
                'success': True,
                'backup_path': str(backup_path),
                'backup_size': backup_path.stat().st_size,
                'backup_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    def restore_database(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore database from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            Restore statistics
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            # Extract and restore from ZIP
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Read metadata
                metadata = json.loads(zipf.read('metadata.json').decode())

                # Extract database dump
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as tmp:
                    tmp.write(zipf.read('database_dump.sql').decode())
                    tmp_path = tmp.name

                # Restore database
                with self.db.get_connection() as conn:
                    # Clear existing data
                    conn.execute("DROP TABLE IF EXISTS primitive_rules")
                    conn.execute("DROP TABLE IF EXISTS semantic_rules")
                    conn.execute("DROP TABLE IF EXISTS task_rules")
                    conn.execute("DROP TABLE IF EXISTS semantic_primitive_relations")
                    conn.execute("DROP TABLE IF EXISTS task_semantic_relations")
                    conn.execute("DROP TABLE IF EXISTS rule_versions")
                    conn.execute("DROP TABLE IF EXISTS rule_tags")
                    conn.execute("DROP TABLE IF EXISTS tags")
                    conn.execute("DROP TABLE IF EXISTS migrations")

                    # Execute restore script
                    with open(tmp_path, 'r') as f:
                        restore_sql = f.read()
                    conn.executescript(restore_sql)

                # Clean up temp file
                Path(tmp_path).unlink()

            return {
                'success': True,
                'restore_date': datetime.now().isoformat(),
                'original_backup_date': metadata['backup_date'],
                'statistics': self._get_database_stats()
            }

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise

    def _export_json(self, filepath: str, rule_types: List[str]) -> Dict[str, Any]:
        """Export rules to JSON format."""
        data = self._export_all_rules(rule_types)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            'success': True,
            'format': 'json',
            'filepath': filepath,
            'exported_rules': sum(len(rules) for rules in data['rules'].values())
        }

    def _export_yaml(self, filepath: str, rule_types: List[str]) -> Dict[str, Any]:
        """Export rules to YAML format."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML export. Install with: pip install pyyaml")

        data = self._export_all_rules(rule_types)

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        return {
            'success': True,
            'format': 'yaml',
            'filepath': filepath,
            'exported_rules': sum(len(rules) for rules in data['rules'].values())
        }

    def _export_sql(self, filepath: str, rule_types: List[str]) -> Dict[str, Any]:
        """Export rules to SQL format."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("-- AI Prompt Engineering System Rules Export\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")

            exported_count = 0

            # Export each rule type
            for rule_type in rule_types:
                table_name = f"{rule_type}_rules"

                # Get rules
                rules = self.db.execute_query(f"SELECT * FROM {table_name}")

                if rules:
                    f.write(f"-- {rule_type.title()} Rules\n")
                    for rule in rules:
                        # Generate INSERT statement
                        columns = list(rule.keys())
                        values = [self._sql_escape(rule[col]) for col in columns]

                        f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                        exported_count += 1

                    f.write("\n")

            # Export relationships
            if 'semantic' in rule_types and 'primitive' in rule_types:
                relations = self.db.execute_query("SELECT * FROM semantic_primitive_relations")
                if relations:
                    f.write("-- Semantic-Primitive Relations\n")
                    for rel in relations:
                        columns = list(rel.keys())
                        values = [self._sql_escape(rel[col]) for col in columns]
                        f.write(f"INSERT INTO semantic_primitive_relations ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                    f.write("\n")

            if 'task' in rule_types and 'semantic' in rule_types:
                relations = self.db.execute_query("SELECT * FROM task_semantic_relations")
                if relations:
                    f.write("-- Task-Semantic Relations\n")
                    for rel in relations:
                        columns = list(rel.keys())
                        values = [self._sql_escape(rel[col]) for col in columns]
                        f.write(f"INSERT INTO task_semantic_relations ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                    f.write("\n")

        return {
            'success': True,
            'format': 'sql',
            'filepath': filepath,
            'exported_rules': exported_count
        }

    def _import_json(self, filepath: str, merge_strategy: str) -> Dict[str, Any]:
        """Import rules from JSON format."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return self._import_rules_data(data, merge_strategy)

    def _import_yaml(self, filepath: str, merge_strategy: str) -> Dict[str, Any]:
        """Import rules from YAML format."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML import. Install with: pip install pyyaml")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return self._import_rules_data(data, merge_strategy)

    def _import_sql(self, filepath: str, merge_strategy: str) -> Dict[str, Any]:
        """Import rules from SQL format."""
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        imported_count = 0

        with self.db.get_connection() as conn:
            # Execute SQL statements
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(statement)
                        if statement.upper().startswith('INSERT'):
                            imported_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to execute SQL statement: {e}")

        return {
            'success': True,
            'format': 'sql',
            'imported_rules': imported_count,
            'merge_strategy': merge_strategy
        }

    def _import_rules_data(self, data: Dict[str, Any], merge_strategy: str) -> Dict[str, Any]:
        """Import rules from parsed data."""
        imported_count = 0
        skipped_count = 0

        # Import each rule type
        for rule_type, rules in data.get('rules', {}).items():
            table_name = f"{rule_type}_rules"

            for rule in rules:
                # Check if rule exists
                existing = self.db.execute_query(
                    f"SELECT id FROM {table_name} WHERE name = ?",
                    (rule['name'],)
                )

                if existing:
                    if merge_strategy == 'skip_existing':
                        skipped_count += 1
                        continue
                    elif merge_strategy == 'overwrite':
                        # Update existing rule
                        self._update_rule(table_name, existing[0]['id'], rule)
                        imported_count += 1
                    elif merge_strategy == 'create_new':
                        # Create with new name
                        rule['name'] = f"{rule['name']}_imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        self._create_rule(table_name, rule)
                        imported_count += 1
                else:
                    # Create new rule
                    self._create_rule(table_name, rule)
                    imported_count += 1

        return {
            'success': True,
            'imported_rules': imported_count,
            'skipped_rules': skipped_count,
            'merge_strategy': merge_strategy
        }

    def _export_all_rules(self, rule_types: List[str] = None) -> Dict[str, Any]:
        """Export all rules to a dictionary."""
        if rule_types is None:
            rule_types = ['primitive', 'semantic', 'task']

        data = {
            'export_date': datetime.now().isoformat(),
            'version': '1.0',
            'rules': {},
            'relationships': {}
        }

        # Export rules
        for rule_type in rule_types:
            table_name = f"{rule_type}_rules"
            rules = self.db.execute_query(f"SELECT * FROM {table_name}")
            data['rules'][rule_type] = rules

        # Export relationships
        if 'semantic' in rule_types and 'primitive' in rule_types:
            data['relationships']['semantic_primitive'] = self.db.execute_query(
                "SELECT * FROM semantic_primitive_relations"
            )

        if 'task' in rule_types and 'semantic' in rule_types:
            data['relationships']['task_semantic'] = self.db.execute_query(
                "SELECT * FROM task_semantic_relations"
            )

        return data

    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}

        # Count rules
        for rule_type in ['primitive', 'semantic', 'task']:
            count = self.db.execute_query(f"SELECT COUNT(*) as count FROM {rule_type}_rules")[0]['count']
            stats[f"{rule_type}_count"] = count

        # Count relationships
        stats['semantic_primitive_relations'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM semantic_primitive_relations"
        )[0]['count']

        stats['task_semantic_relations'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM task_semantic_relations"
        )[0]['count']

        return stats

    def _sql_escape(self, value: Any) -> str:
        """Escape value for SQL insertion."""
        if value is None:
            return 'NULL'
        elif isinstance(value, str):
            return f"'{value.replace(chr(39), chr(39) + chr(39))}'"  # Escape single quotes
        elif isinstance(value, bool):
            return '1' if value else '0'
        else:
            return str(value)

    def _create_rule(self, table_name: str, rule: Dict[str, Any]):
        """Create a new rule in the database."""
        columns = [col for col in rule.keys() if col != 'id']
        values = [rule[col] for col in columns]
        placeholders = ['?' for _ in columns]

        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        self.db.execute_insert(query, tuple(values))

    def _update_rule(self, table_name: str, rule_id: int, rule: Dict[str, Any]):
        """Update an existing rule in the database."""
        columns = [col for col in rule.keys() if col != 'id']
        values = [rule[col] for col in columns]
        set_clause = ', '.join([f"{col} = ?" for col in columns])

        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        self.db.execute_query(query, tuple(values + [rule_id]))
