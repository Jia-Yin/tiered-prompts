"""
TemplateEngine: Handles variable substitution and context injection using Jinja2.
"""

import logging
from typing import Dict, Any, Optional, List
from jinja2 import Template, Environment, DictLoader, select_autoescape, TemplateSyntaxError
import json

logger = logging.getLogger(__name__)


class TemplateEngine:
    def __init__(self):
        """Initialize the template engine with Jinja2 environment."""
        self.env = Environment(
            loader=DictLoader({}),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.env.filters['json_pretty'] = self._json_pretty_filter
        self.env.filters['truncate_words'] = self._truncate_words_filter
        self.env.filters['upper_first'] = self._upper_first_filter

    def render_template(self, template_str: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template string with the given context.

        Args:
            template_str: Jinja2 template string
            context: Dictionary of variables for template rendering

        Returns:
            Rendered template string
        """
        if context is None:
            context = {}

        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error: {e}")
            raise ValueError(f"Invalid template syntax: {e}")
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise ValueError(f"Template rendering failed: {e}")

    def render_rule_hierarchy(self, resolved_hierarchy: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Render a complete rule hierarchy into a final prompt.

        Args:
            resolved_hierarchy: Result from RuleResolver
            context: Additional context for rendering

        Returns:
            Final rendered prompt
        """
        if context is None:
            context = {}

        # Merge context from hierarchy
        merged_context = {**resolved_hierarchy.get('context', {}), **context}

        # Start with task rule
        task_rule = resolved_hierarchy.get('task_rule')
        if not task_rule:
            raise ValueError("No task rule found in hierarchy")

        # Build semantic rules content dynamically
        semantic_rules_content = []
        all_primitive_rules_content = []

        for semantic_data in resolved_hierarchy.get('semantic_rules', []):
            # Render this semantic rule with its primitive rules
            rendered_semantic = self._render_semantic_rule_with_primitives(semantic_data, merged_context)
            semantic_rules_content.append(rendered_semantic)

            # Also collect all primitive rules for the task level
            for primitive_rule in semantic_data.get('primitive_rules', []):
                if primitive_rule.get('content'):
                    rendered_primitive = self._render_primitive_rule(primitive_rule, merged_context)
                    if rendered_primitive and rendered_primitive not in all_primitive_rules_content:
                        all_primitive_rules_content.append(rendered_primitive)

        # Add dynamic content to context
        merged_context['semantic_rules'] = '\n\n---\n\n'.join(semantic_rules_content)
        merged_context['primitive_rules'] = '\n\n'.join(all_primitive_rules_content)

        # Render final task template
        try:
            return self.render_template(task_rule['prompt_template'], merged_context)
        except Exception as e:
            logger.error(f"Error rendering task rule {task_rule['id']}: {e}")
            raise

    def _render_semantic_rule_with_primitives(self, semantic_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render a semantic rule with its associated primitive rules dynamically embedded."""
        semantic_rule = semantic_data.get('semantic_rule')
        if not semantic_rule:
            return ""

        # Build primitive rules content for this semantic rule
        primitive_rules_content = []
        for primitive_rule in semantic_data.get('primitive_rules', []):
            if primitive_rule.get('content'):
                rendered_primitive = self._render_primitive_rule(primitive_rule, context)
                if rendered_primitive:
                    primitive_rules_content.append(f"- {rendered_primitive}")

        # Create context with primitive rules for this semantic rule
        semantic_context = {
            **context,
            'primitive_rules': '\n'.join(primitive_rules_content) if primitive_rules_content else ''
        }

        # Render semantic template
        try:
            return self.render_template(semantic_rule['content_template'], semantic_context)
        except Exception as e:
            logger.error(f"Error rendering semantic rule {semantic_rule['id']}: {e}")
            return f"<!-- Error rendering semantic rule {semantic_rule['name']}: {e} -->"

    def _render_primitive_rule(self, primitive_rule: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render a primitive rule."""
        if not primitive_rule.get('content'):
            return ""

        # Primitive rules may contain simple templates too
        try:
            return self.render_template(primitive_rule['content'], context)
        except Exception as e:
            logger.error(f"Error rendering primitive rule {primitive_rule['id']}: {e}")
            return primitive_rule['content']  # Return as-is if template fails

    def validate_template(self, template_str: str) -> Dict[str, Any]:
        """
        Validate a template string for syntax errors.

        Args:
            template_str: Template string to validate

        Returns:
            Dictionary with validation results
        """
        try:
            template = self.env.from_string(template_str)

            return {
                'valid': True,
                'variables': self._extract_variables(template_str),
                'errors': []
            }
        except TemplateSyntaxError as e:
            return {
                'valid': False,
                'variables': [],
                'errors': [str(e)]
            }
        except Exception as e:
            return {
                'valid': False,
                'variables': [],
                'errors': [f"Unexpected error: {e}"]
            }

    def _extract_variables(self, template_str: str) -> List[str]:
        """Extract variable names from a template string."""
        try:
            # Parse the template and extract variable names
            from jinja2 import nodes
            ast = self.env.parse(template_str)
            variables = set()

            # Walk the AST to find Name nodes (variables)
            for node in ast.find_all(nodes.Name):
                variables.add(node.name)

            return sorted(list(variables))
        except Exception as e:
            logger.warning(f"Could not extract variables from template: {e}")
            return []

    def render_with_model_format(self, content: str, model_type: str = "claude") -> str:
        """
        Format content for specific AI models.

        Args:
            content: Raw content to format
            model_type: Target model type ('claude', 'gpt', 'gemini')

        Returns:
            Formatted content for the specific model
        """
        model_formats = {
            'claude': self._format_for_claude,
            'gpt': self._format_for_gpt,
            'gemini': self._format_for_gemini
        }

        formatter = model_formats.get(model_type.lower(), self._format_default)
        return formatter(content)

    def _format_for_claude(self, content: str) -> str:
        """Format content for Claude (Anthropic)."""
        return f"<thinking>\nProcessing the following prompt requirements:\n</thinking>\n\n{content}"

    def _format_for_gpt(self, content: str) -> str:
        """Format content for GPT (OpenAI)."""
        return f"System: You are a helpful assistant following these guidelines:\n\n{content}"

    def _format_for_gemini(self, content: str) -> str:
        """Format content for Gemini (Google)."""
        return f"Instructions: Please follow these guidelines carefully:\n\n{content}"

    def _format_default(self, content: str) -> str:
        """Default formatting."""
        return content

    # Custom Jinja2 filters
    def _json_pretty_filter(self, value: Any) -> str:
        """Pretty print JSON."""
        try:
            return json.dumps(value, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)

    def _truncate_words_filter(self, value: str, length: int = 50) -> str:
        """Truncate text to specified number of words."""
        if not isinstance(value, str):
            return str(value)

        words = value.split()
        if len(words) <= length:
            return value

        return ' '.join(words[:length]) + '...'

    def _upper_first_filter(self, value: str) -> str:
        """Capitalize first letter of string."""
        if not isinstance(value, str) or not value:
            return value

        return value[0].upper() + value[1:] if len(value) > 1 else value.upper()
