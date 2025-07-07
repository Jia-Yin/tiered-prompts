import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import {
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { createRule, updateRule, getRule } from '../services/api';
import { CreateRuleRequest, UpdateRuleRequest, Rule } from '../types';
import { handleApiError } from '../services/api';

const RuleEditor: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = id !== undefined && id !== 'new';

  const [formData, setFormData] = useState<CreateRuleRequest>({
    rule_type: 'primitive',
    name: '',
    content: '',
    description: '',
    category: '',
    language: '',
    framework: '',
    domain: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch existing rule if editing
  const { data: existingRule, isLoading } = useQuery(
    ['rule', id],
    () => getRule(parseInt(id!)),
    {
      enabled: isEditing && !isNaN(parseInt(id!)),
      onSuccess: (rule: Rule) => {
        setFormData({
          rule_type: rule.type,
          name: rule.name,
          content: rule.content || '',
          description: rule.description || '',
          category: rule.category || '',
          language: rule.language || '',
          framework: rule.framework || '',
          domain: rule.domain || ''
        });
      }
    }
  );

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required';
    }

    if (formData.rule_type === 'task') {
      if (!formData.language?.trim()) {
        newErrors.language = 'Language is required for task rules';
      }
      if (!formData.domain?.trim()) {
        newErrors.domain = 'Domain is required for task rules';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      if (isEditing) {
        const updateData: UpdateRuleRequest = {
          name: formData.name,
          content: formData.content,
          description: formData.description,
          category: formData.category
        };

        if (formData.rule_type === 'task') {
          updateData.language = formData.language;
          updateData.framework = formData.framework;
          updateData.domain = formData.domain;
        }

        await updateRule(parseInt(id!), updateData);
      } else {
        await createRule(formData);
      }

      // Force refetch rules data
      await queryClient.invalidateQueries(['rules']);
      await queryClient.refetchQueries(['rules']);
      
      // Navigate back to rules list
      navigate('/rules');
    } catch (error) {
      console.error('Error saving rule:', error);
      setErrors({ submit: handleApiError(error) });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  if (isEditing && isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-4" />
          <div className="text-gray-500">Loading rule...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="page-header mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/rules')}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-md"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEditing ? 'Edit Rule' : 'Create New Rule'}
            </h1>
            <p className="text-gray-600">
              {isEditing ? 'Modify the rule details below' : 'Fill in the details to create a new rule'}
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow-sm rounded-lg p-6">
          {/* Rule Type */}
          <div className="mb-6">
            <label htmlFor="rule_type" className="block text-sm font-medium text-gray-700 mb-2">
              Rule Type
            </label>
            <select
              id="rule_type"
              name="rule_type"
              value={formData.rule_type}
              onChange={handleInputChange}
              disabled={isEditing} // Disable when editing existing rule
              className={`input-field ${isEditing ? 'bg-gray-100 cursor-not-allowed' : ''}`}
            >
              <option value="primitive">Primitive Rule</option>
              <option value="semantic">Semantic Rule</option>
              <option value="task">Task Rule</option>
            </select>
            <p className="mt-1 text-sm text-gray-500">
              {formData.rule_type === 'primitive' && 'Basic formatting and structure rules'}
              {formData.rule_type === 'semantic' && 'Content and meaning rules'}
              {formData.rule_type === 'task' && 'Complete workflow templates'}
            </p>
          </div>

          {/* Name */}
          <div className="mb-6">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Name *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className={`input-field ${errors.name ? 'border-red-500' : ''}`}
              placeholder="Enter a unique name for this rule"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
          </div>

          {/* Content */}
          <div className="mb-6">
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              Content *
            </label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleInputChange}
              rows={8}
              className={`input-field ${errors.content ? 'border-red-500' : ''}`}
              placeholder={
                formData.rule_type === 'primitive' ? 'Enter the rule content...' :
                formData.rule_type === 'semantic' ? 'Enter the content template...' :
                'Enter the prompt template...'
              }
            />
            {errors.content && (
              <p className="mt-1 text-sm text-red-600">{errors.content}</p>
            )}
          </div>

          {/* Description */}
          <div className="mb-6">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className="input-field"
              placeholder="Describe what this rule does..."
            />
          </div>

          {/* Category */}
          <div className="mb-6">
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <input
              type="text"
              id="category"
              name="category"
              value={formData.category}
              onChange={handleInputChange}
              className="input-field"
              placeholder="e.g., formatting, validation, workflow"
            />
          </div>

          {/* Task-specific fields */}
          {formData.rule_type === 'task' && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Task Rule Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-2">
                    Language *
                  </label>
                  <input
                    type="text"
                    id="language"
                    name="language"
                    value={formData.language}
                    onChange={handleInputChange}
                    className={`input-field ${errors.language ? 'border-red-500' : ''}`}
                    placeholder="e.g., Python, JavaScript, TypeScript"
                  />
                  {errors.language && (
                    <p className="mt-1 text-sm text-red-600">{errors.language}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="framework" className="block text-sm font-medium text-gray-700 mb-2">
                    Framework
                  </label>
                  <input
                    type="text"
                    id="framework"
                    name="framework"
                    value={formData.framework}
                    onChange={handleInputChange}
                    className="input-field"
                    placeholder="e.g., React, FastAPI, Django"
                  />
                </div>

                <div>
                  <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
                    Domain *
                  </label>
                  <input
                    type="text"
                    id="domain"
                    name="domain"
                    value={formData.domain}
                    onChange={handleInputChange}
                    className={`input-field ${errors.domain ? 'border-red-500' : ''}`}
                    placeholder="e.g., web_dev, data_science, api_dev"
                  />
                  {errors.domain && (
                    <p className="mt-1 text-sm text-red-600">{errors.domain}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
              <div className="text-sm text-red-700">{errors.submit}</div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/rules')}
            className="btn-secondary"
          >
            <XMarkIcon className="h-5 w-5 mr-2" />
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary"
          >
            {isSubmitting ? (
              <>
                <div className="spinner w-4 h-4 mr-2" />
                {isEditing ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              <>
                <CheckIcon className="h-5 w-5 mr-2" />
                {isEditing ? 'Update Rule' : 'Create Rule'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RuleEditor;