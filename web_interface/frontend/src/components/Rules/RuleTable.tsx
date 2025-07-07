import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { PencilIcon, TrashIcon, PlayIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { useQueryClient } from 'react-query';
import { Rule } from '../../types';
import { deleteRule, handleApiError } from '../../services/api';

interface RuleTableProps {
  rules: Rule[];
  onUpdate: () => void;
  onRuleClick: (rule: Rule) => void;
}

const RuleTable: React.FC<RuleTableProps> = ({ rules, onUpdate, onRuleClick }) => {
  const [deletingRules, setDeletingRules] = useState<Set<number>>(new Set());
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

  const handleDelete = async (e: React.MouseEvent, rule: Rule) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete "${rule.name}"? This action cannot be undone.`)) {
      return;
    }

    setDeletingRules(prev => new Set(prev).add(rule.id));
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
      setDeletingRules(prev => {
        const newSet = new Set(prev);
        newSet.delete(rule.id);
        return newSet;
      });
    }
  };

  const handleGeneratePrompt = (e: React.MouseEvent, rule: Rule) => {
    e.stopPropagation();
    // Navigate to playground with the rule pre-selected
    navigate('/playground', { state: { selectedRule: rule } });
  };

  const handleManageRelationships = () => {
    // Navigate to relationships page
    navigate('/relationships');
  };

  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Rules</h3>
        <button
          onClick={handleManageRelationships}
          className="btn-secondary flex items-center text-sm"
        >
          <ArrowRightIcon className="h-4 w-4 mr-2" />
          Manage Relationships
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Content
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rules.map((rule) => (
              <tr key={`${rule.type}-${rule.id}`} onClick={() => onRuleClick(rule)} className="cursor-pointer hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {rule.name}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRuleTypeColor(rule.type)}`}>
                    {rule.type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-xs truncate">
                    {rule.content || 'No content available'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {rule.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    {(rule.type === 'semantic' || rule.type === 'task') && (
                      <button
                        onClick={(e) => handleGeneratePrompt(e, rule)}
                        className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                        title="Generate Prompt"
                      >
                        <PlayIcon className="h-4 w-4" />
                      </button>
                    )}
                    <Link
                      to={`/rules/${rule.id}/edit`}
                      onClick={(e) => e.stopPropagation()}
                      className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      title="Edit Rule"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </Link>
                    <button
                      onClick={(e) => handleDelete(e, rule)}
                      disabled={deletingRules.has(rule.id)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                      title="Delete Rule"
                    >
                      {deletingRules.has(rule.id) ? (
                        <div className="w-4 h-4 border-2 border-gray-300 border-t-red-500 rounded-full animate-spin" />
                      ) : (
                        <TrashIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RuleTable;