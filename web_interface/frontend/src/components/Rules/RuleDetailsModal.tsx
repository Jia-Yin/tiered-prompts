import React from 'react';
import { Rule } from '../../types';

interface RuleDetailsModalProps {
  rule: Rule | null;
  dependencies: any | null;
  onClose: () => void;
}

const RuleDetailsModal: React.FC<RuleDetailsModalProps> = ({ rule, dependencies, onClose }) => {
  if (!rule) return null;

  const getRelationName = (relation: any) => {
    return relation.name || relation.task_name || relation.semantic_name || relation.primitive_name || 'Unknown Rule';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl">
        <div className="flex justify-between items-center border-b pb-3">
          <h2 className="text-2xl font-bold">{rule.name}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">&times;</button>
        </div>
        <div className="mt-4">
          <p><strong>Type:</strong> {rule.type}</p>
          <p><strong>Description:</strong> {rule.description}</p>
          <div className="mt-4">
            <h3 className="text-xl font-bold">Content</h3>
            <pre className="bg-gray-100 p-4 rounded-md mt-2 whitespace-pre-wrap">{rule.content}</pre>
          </div>
          {dependencies && (
            <div className="mt-4">
              <h3 className="text-xl font-bold">Relationships</h3>
              <div className="mt-2">
                <h4 className="font-bold">Parents</h4>
                {dependencies.parents.length > 0 ? (
                  <ul className="list-disc list-inside">
                    {dependencies.parents.map((parent: any) => (
                      <li key={parent.id}>{getRelationName(parent)} ({parent.type})</li>
                    ))}
                  </ul>
                ) : (
                  <p>No parents</p>
                )}
              </div>
              <div className="mt-2">
                <h4 className="font-bold">Children</h4>
                {dependencies.children.length > 0 ? (
                  <ul className="list-disc list-inside">
                    {dependencies.children.map((child: any) => (
                      <li key={child.id}>{getRelationName(child)} (ID: {child.id}, Type: {child.type})</li>
                    ))}
                  </ul>
                ) : (
                  <p>No children</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RuleDetailsModal;
