"""
Sample seed data for testing the AI Prompt Engineering System.
"""

import logging
from typing import Dict, List, Any

from .crud import (
    primitive_crud, semantic_crud, task_crud,
    relation_crud, tag_crud
)

logger = logging.getLogger(__name__)


class SeedDataManager:
    """Manages sample data creation for testing and development."""

    def __init__(self):
        self.created_ids = {
            'primitive': {},
            'semantic': {},
            'task': {}
        }

    def create_sample_primitive_rules(self) -> Dict[str, int]:
        """Create sample primitive rules."""
        primitive_rules = [
            {
                'name': 'clear_instructions',
                'description': 'Provide clear and specific instructions',
                'content': 'Be specific and clear in your instructions. Avoid ambiguous language.',
                'category': 'instruction'
            },
            {
                'name': 'structured_format',
                'description': 'Use structured output format',
                'content': 'Format your response using headers, bullet points, and clear sections.',
                'category': 'format'
            },
            {
                'name': 'code_quality_constraint',
                'description': 'Ensure high code quality standards',
                'content': 'Follow best practices, use meaningful variable names, and include error handling.',
                'category': 'constraint'
            },
            {
                'name': 'step_by_step_pattern',
                'description': 'Break down complex tasks into steps',
                'content': 'Provide step-by-step explanations for complex procedures.',
                'category': 'pattern'
            },
            {
                'name': 'example_inclusion',
                'description': 'Include relevant examples',
                'content': 'Provide concrete examples to illustrate concepts and solutions.',
                'category': 'pattern'
            },
            {
                'name': 'error_prevention',
                'description': 'Focus on preventing common errors',
                'content': 'Highlight potential pitfalls and how to avoid them.',
                'category': 'constraint'
            }
        ]

        created = {}
        for rule in primitive_rules:
            try:
                rule_id = primitive_crud.create_primitive_rule(**rule)
                created[rule['name']] = rule_id
                logger.info(f"Created primitive rule: {rule['name']} (ID: {rule_id})")
            except Exception as e:
                logger.error(f"Failed to create primitive rule {rule['name']}: {e}")

        self.created_ids['primitive'] = created
        return created

    def create_sample_semantic_rules(self) -> Dict[str, int]:
        """Create sample semantic rules."""
        semantic_rules = [
            {
                'name': 'code_review_template',
                'description': 'Template for conducting code reviews',
                'content_template': '''
Review the following code for:
1. Functionality and correctness
2. Code quality and best practices
3. Security considerations
4. Performance implications

Code to review:
{{code_snippet}}

Focus areas: {{focus_areas}}

Guidelines to follow:
{{primitive_rules}}
''',
                'category': 'code_review'
            },
            {
                'name': 'debugging_assistant',
                'description': 'Template for debugging assistance',
                'content_template': '''
Help debug the following issue:

Problem description: {{problem_description}}
Error message: {{error_message}}
Code context: {{code_context}}

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Suggested fixes
4. Prevention strategies

Guidelines to follow:
{{primitive_rules}}
''',
                'category': 'debugging'
            },
            {
                'name': 'concept_explanation',
                'description': 'Template for explaining technical concepts',
                'content_template': '''
Explain the concept of {{concept_name}} in {{context}}.

Include:
- Definition and purpose
- Key components or principles
- Real-world examples
- Common use cases
- Best practices

Target audience: {{audience_level}}

Guidelines to follow:
{{primitive_rules}}
''',
                'category': 'explanation'
            },
            {
                'name': 'optimization_guide',
                'description': 'Template for optimization recommendations',
                'content_template': '''
Analyze and optimize the following {{optimization_target}}:

Current implementation: {{current_code}}
Performance requirements: {{requirements}}
Constraints: {{constraints}}

Provide:
1. Performance analysis
2. Optimization opportunities
3. Recommended improvements
4. Trade-offs and considerations

Guidelines to follow:
{{primitive_rules}}
''',
                'category': 'optimization'
            }
        ]

        created = {}
        for rule in semantic_rules:
            try:
                rule_id = semantic_crud.create_semantic_rule(**rule)
                created[rule['name']] = rule_id
                logger.info(f"Created semantic rule: {rule['name']} (ID: {rule_id})")
            except Exception as e:
                logger.error(f"Failed to create semantic rule {rule['name']}: {e}")

        self.created_ids['semantic'] = created
        return created

    def create_sample_task_rules(self) -> Dict[str, int]:
        """Create sample task rules."""
        task_rules = [
            {
                'name': 'react_component_review',
                'description': 'Review React component code',
                'prompt_template': '''
You are an expert React developer. Review the following React component for best practices, performance, and maintainability.

Component: {{component_name}}
Framework version: {{react_version}}

{{semantic_rules}}

{{primitive_rules}}

Provide specific recommendations for improvement.
''',
                'language': 'javascript',
                'framework': 'react',
                'domain': 'web_dev'
            },
            {
                'name': 'python_data_analysis',
                'description': 'Python data analysis task',
                'prompt_template': '''
You are a data science expert. Help with the following Python data analysis task.

Dataset: {{dataset_description}}
Analysis goal: {{analysis_goal}}
Libraries: {{libraries}}

{{semantic_rules}}

{{primitive_rules}}

Provide complete code with explanations.
''',
                'language': 'python',
                'framework': 'pandas',
                'domain': 'data_science'
            },
            {
                'name': 'api_design_review',
                'description': 'RESTful API design review',
                'prompt_template': '''
You are an API design expert. Review the following API design for RESTful principles and best practices.

API specification: {{api_spec}}
Use case: {{use_case}}
Scale requirements: {{scale_requirements}}

{{semantic_rules}}

{{primitive_rules}}

Focus on security, scalability, and developer experience.
''',
                'language': 'general',
                'framework': 'rest',
                'domain': 'web_dev'
            },
            {
                'name': 'database_optimization',
                'description': 'Database query optimization',
                'prompt_template': '''
You are a database optimization expert. Analyze and optimize the following database queries.

Database type: {{db_type}}
Current queries: {{queries}}
Performance issues: {{performance_issues}}
Data volume: {{data_volume}}

{{semantic_rules}}

{{primitive_rules}}

Provide optimized queries with explanations.
''',
                'language': 'sql',
                'framework': 'general',
                'domain': 'data_science'
            }
        ]

        created = {}
        for rule in task_rules:
            try:
                rule_id = task_crud.create_task_rule(**rule)
                created[rule['name']] = rule_id
                logger.info(f"Created task rule: {rule['name']} (ID: {rule_id})")
            except Exception as e:
                logger.error(f"Failed to create task rule {rule['name']}: {e}")

        self.created_ids['task'] = created
        return created

    def create_sample_relationships(self):
        """Create sample relationships between rules."""
        primitive_ids = self.created_ids['primitive']
        semantic_ids = self.created_ids['semantic']
        task_ids = self.created_ids['task']

        # Semantic-Primitive relationships
        semantic_primitive_relations = [
            # Code review template uses multiple primitives
            ('code_review_template', 'clear_instructions', 1.0, 0, True),
            ('code_review_template', 'structured_format', 0.9, 1, True),
            ('code_review_template', 'code_quality_constraint', 1.0, 2, True),
            ('code_review_template', 'example_inclusion', 0.7, 3, False),

            # Debugging assistant
            ('debugging_assistant', 'step_by_step_pattern', 1.0, 0, True),
            ('debugging_assistant', 'clear_instructions', 0.8, 1, True),
            ('debugging_assistant', 'error_prevention', 0.9, 2, True),

            # Concept explanation
            ('concept_explanation', 'structured_format', 1.0, 0, True),
            ('concept_explanation', 'example_inclusion', 1.0, 1, True),
            ('concept_explanation', 'step_by_step_pattern', 0.8, 2, False),

            # Optimization guide
            ('optimization_guide', 'clear_instructions', 0.9, 0, True),
            ('optimization_guide', 'code_quality_constraint', 1.0, 1, True),
            ('optimization_guide', 'structured_format', 0.8, 2, True),
        ]

        for semantic_name, primitive_name, weight, order, required in semantic_primitive_relations:
            if semantic_name in semantic_ids and primitive_name in primitive_ids:
                try:
                    relation_crud.create_semantic_primitive_relation(
                        semantic_ids[semantic_name],
                        primitive_ids[primitive_name],
                        weight, order, required
                    )
                    logger.info(f"Created semantic-primitive relation: {semantic_name} -> {primitive_name}")
                except Exception as e:
                    logger.error(f"Failed to create relation {semantic_name} -> {primitive_name}: {e}")

        # Task-Semantic relationships
        task_semantic_relations = [
            # React component review
            ('react_component_review', 'code_review_template', 1.0, 0, True),
            ('react_component_review', 'optimization_guide', 0.7, 1, False),

            # Python data analysis
            ('python_data_analysis', 'concept_explanation', 0.8, 0, True),
            ('python_data_analysis', 'code_review_template', 0.6, 1, False),

            # API design review
            ('api_design_review', 'code_review_template', 1.0, 0, True),
            ('api_design_review', 'optimization_guide', 0.8, 1, True),

            # Database optimization
            ('database_optimization', 'optimization_guide', 1.0, 0, True),
            ('database_optimization', 'debugging_assistant', 0.6, 1, False),
        ]

        for task_name, semantic_name, weight, order, required in task_semantic_relations:
            if task_name in task_ids and semantic_name in semantic_ids:
                try:
                    relation_crud.create_task_semantic_relation(
                        task_ids[task_name],
                        semantic_ids[semantic_name],
                        weight, order, required
                    )
                    logger.info(f"Created task-semantic relation: {task_name} -> {semantic_name}")
                except Exception as e:
                    logger.error(f"Failed to create relation {task_name} -> {semantic_name}: {e}")

    def create_sample_tags(self):
        """Create sample tags for rules."""
        primitive_ids = self.created_ids['primitive']
        semantic_ids = self.created_ids['semantic']
        task_ids = self.created_ids['task']

        # Tags for primitive rules
        primitive_tags = {
            'clear_instructions': ['clarity', 'communication', 'best-practice'],
            'structured_format': ['formatting', 'organization', 'readability'],
            'code_quality_constraint': ['quality', 'standards', 'best-practice'],
            'step_by_step_pattern': ['methodology', 'clarity', 'tutorial'],
            'example_inclusion': ['examples', 'clarity', 'tutorial'],
            'error_prevention': ['reliability', 'quality', 'debugging']
        }

        for rule_name, tags in primitive_tags.items():
            if rule_name in primitive_ids:
                for tag in tags:
                    try:
                        tag_crud.add_tag('primitive', primitive_ids[rule_name], tag)
                    except Exception as e:
                        logger.error(f"Failed to add tag {tag} to {rule_name}: {e}")

        # Tags for semantic rules
        semantic_tags = {
            'code_review_template': ['code-review', 'template', 'quality'],
            'debugging_assistant': ['debugging', 'troubleshooting', 'assistant'],
            'concept_explanation': ['education', 'explanation', 'tutorial'],
            'optimization_guide': ['performance', 'optimization', 'analysis']
        }

        for rule_name, tags in semantic_tags.items():
            if rule_name in semantic_ids:
                for tag in tags:
                    try:
                        tag_crud.add_tag('semantic', semantic_ids[rule_name], tag)
                    except Exception as e:
                        logger.error(f"Failed to add tag {tag} to {rule_name}: {e}")

        # Tags for task rules
        task_tags = {
            'react_component_review': ['react', 'javascript', 'web-dev', 'component'],
            'python_data_analysis': ['python', 'data-science', 'analysis', 'pandas'],
            'api_design_review': ['api', 'rest', 'design', 'web-dev'],
            'database_optimization': ['database', 'sql', 'optimization', 'performance']
        }

        for rule_name, tags in task_tags.items():
            if rule_name in task_ids:
                for tag in tags:
                    try:
                        tag_crud.add_tag('task', task_ids[rule_name], tag)
                    except Exception as e:
                        logger.error(f"Failed to add tag {tag} to {rule_name}: {e}")

    def create_all_sample_data(self) -> Dict[str, Any]:
        """Create all sample data."""
        logger.info("Creating sample data...")

        results = {
            'primitive_rules': self.create_sample_primitive_rules(),
            'semantic_rules': self.create_sample_semantic_rules(),
            'task_rules': self.create_sample_task_rules()
        }

        # Create relationships and tags
        self.create_sample_relationships()
        self.create_sample_tags()

        logger.info("Sample data creation completed")
        return results

    def clear_all_data(self):
        """Clear all data from the database (for testing)."""
        from .connection import db_manager

        tables = [
            'rule_tags',
            'rule_versions',
            'task_semantic_relations',
            'semantic_primitive_relations',
            'task_rules',
            'semantic_rules',
            'primitive_rules'
        ]

        for table in tables:
            try:
                db_manager.execute_update(f"DELETE FROM {table}")
                logger.info(f"Cleared table: {table}")
            except Exception as e:
                logger.error(f"Failed to clear table {table}: {e}")


# Global seed data manager instance
seed_manager = SeedDataManager()


def generate_sample_data():
    """Create sample data for development and testing."""
    return seed_manager.create_all_sample_data()


def clear_sample_data():
    """Clear all sample data."""
    seed_manager.clear_all_data()


if __name__ == "__main__":
    # Create sample data when run directly
    from .connection import initialize_database

    initialize_database()
    results = generate_sample_data()
