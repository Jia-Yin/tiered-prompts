import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { PencilIcon, TrashIcon, PlayIcon } from '@heroicons/react/24/outline';
import { useQueryClient } from 'react-query';
import { Rule } from '../../types';
import { deleteRule, handleApiError } from '../../services/api';

interface RuleCardProps {
  rule: Rule;
  onUpdate: () => void;
  onRuleClick: (rule: Rule) => void;
}

const RuleCard: React.FC<RuleCardProps> = ({ rule, onUpdate, onRuleClick }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const getRuleTypeColor = (type: string) => {
    switch (type) {
      case 'primitive':
        return 'bg-blue-100 text-blue-800';
      case 'semantic':
        return 'bg-green-100 text-green-800';
      case 'task':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete "${rule.name}"? This action cannot be undone.`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteRule(rule.id);

      // Force refresh the rules data aggressively
      await queryClient.invalidateQueries(['rules']);
      await queryClient.refetchQueries(['rules']);
      onUpdate(); // Also call the original update function
    } catch (error) {
      console.error('Error deleting rule:', error);
      alert(`Failed to delete rule: ${handleApiError(error)}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleGeneratePrompt = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Navigate to playground with the rule pre-selected
    navigate('/playground', { state: { selectedRule: rule } });
  };

  return (
    <div
      onClick={() => onRuleClick(rule)}
      className="relative group cursor-pointer bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200"
    >
      <div className="absolute top-3 right-3 flex items-center space-x-1 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
        {(rule.type === 'semantic' || rule.type === 'task') && (
          <button
            onClick={handleGeneratePrompt}
            className="p-2 text-gray-500 hover:text-primary-600 bg-gray-100 hover:bg-primary-100 rounded-full shadow-sm border border-gray-200"
            title="Generate Prompt"
          >
            <PlayIcon className="h-5 w-5" />
          </button>
        )}
        <Link
          to={`/rules/${rule.id}/edit`}
          onClick={(e) => e.stopPropagation()}
          className="p-2 text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-full shadow-sm border border-gray-200"
          title="Edit Rule"
        >
          <PencilIcon className="h-5 w-5" />
        </Link>
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="p-2 text-gray-500 hover:text-red-600 bg-gray-100 hover:bg-red-100 rounded-full shadow-sm border border-gray-200 disabled:opacity-50"
          title="Delete Rule"
        >
          {isDeleting ? (
            <div className="w-5 h-5 border-2 border-gray-300 border-t-red-500 rounded-full animate-spin" />
          ) : (
            <TrashIcon className="h-5 w-5" />
          )}
        </button>
      </div>

      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRuleTypeColor(rule.type)}`}>
              {rule.type}
            </span>
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {rule.name}
            </h3>
          </div>
        </div>

        <div className="text-sm text-gray-600 mb-4">
          <p className="line-clamp-3">
            {rule.content || 'No content available'}
          </p>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>ID: {rule.id}</span>
          <span>Last updated: Just now</span>
        </div>
      </div>
    </div>
  );
};

export default RuleCard;