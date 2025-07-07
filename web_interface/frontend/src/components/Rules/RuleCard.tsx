import React from 'react';
import { Link } from 'react-router-dom';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { Rule } from '../../types';

interface RuleCardProps {
  rule: Rule;
  onUpdate: () => void;
}

const RuleCard: React.FC<RuleCardProps> = ({ rule, onUpdate }) => {
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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRuleTypeColor(rule.type)}`}>
              {rule.type}
            </span>
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {rule.name}
            </h3>
          </div>
          <div className="flex items-center space-x-2">
            <Link
              to={`/rules/${rule.id}/edit`}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <PencilIcon className="h-4 w-4" />
            </Link>
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to delete this rule?')) {
                  // TODO: Implement delete functionality
                  console.log('Delete rule:', rule.id);
                }
              }}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
            >
              <TrashIcon className="h-4 w-4" />
            </button>
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