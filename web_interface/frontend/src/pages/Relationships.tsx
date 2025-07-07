import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  PlusIcon,
  TrashIcon,
  ArrowRightIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowsUpDownIcon
} from '@heroicons/react/24/outline';
import { listRules, handleApiError } from '../services/api';
import { Rule } from '../types';

interface Relationship {
  id: number;
  task_rule_id?: number;
  semantic_rule_id: number;
  primitive_rule_id?: number;
  task_name?: string;
  semantic_name: string;
  primitive_name?: string;
  weight: number;
  order_index: number;
  is_required: boolean;
  context_override?: any;
}

interface RelationshipFormData {
  task_rule_id?: number;
  semantic_rule_id?: number;
  primitive_rule_id?: number;
  weight: number;
  order_index: number;
  is_required: boolean;
  context_override?: string;
}

const Relationships: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'task_semantic' | 'semantic_primitive'>('task_semantic');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState<RelationshipFormData>({
    weight: 1.0,
    order_index: 0,
    is_required: true
  });
  const [formErrors, setFormErrors] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterRequired, setFilterRequired] = useState<'all' | 'required' | 'optional'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'weight' | 'order'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const queryClient = useQueryClient();

  // Fetch all rules
  const { data: rules, isLoading: rulesLoading } = useQuery(
    ['rules'],
    () => listRules(),
    {
      select: (data) => data || []
    }
  );

  // Separate rules by type
  const taskRules = rules?.filter(rule => rule.type === 'task') || [];
  const semanticRules = rules?.filter(rule => rule.type === 'semantic') || [];
  const primitiveRules = rules?.filter(rule => rule.type === 'primitive') || [];

  // Fetch task-semantic relationships
  const { data: taskSemanticRelations, isLoading: taskSemanticLoading, refetch: refetchTaskSemantic } = useQuery(
    ['relationships', 'task-semantic'],
    async () => {
      const response = await fetch('http://localhost:3000/api/v1/relationships/task-semantic');
      if (!response.ok) throw new Error('Failed to fetch task-semantic relationships');
      const data = await response.json();
      return data.relations || [];
    }
  );

  // Fetch semantic-primitive relationships
  const { data: semanticPrimitiveRelations, isLoading: semanticPrimitiveLoading, refetch: refetchSemanticPrimitive } = useQuery(
    ['relationships', 'semantic-primitive'],
    async () => {
      const response = await fetch('http://localhost:3000/api/v1/relationships/semantic-primitive');
      if (!response.ok) throw new Error('Failed to fetch semantic-primitive relationships');
      const data = await response.json();
      return data.relations || [];
    }
  );

  // Create relationship mutation
  const createRelationMutation = useMutation(
    async (data: RelationshipFormData) => {
      const endpoint = activeTab === 'task_semantic' 
        ? '/api/v1/relationships/task-semantic'
        : '/api/v1/relationships/semantic-primitive';

      const body = { ...data };
      if (data.context_override) {
        try {
          body.context_override = JSON.parse(data.context_override);
        } catch (e) {
          throw new Error('Invalid JSON in context override');
        }
      }

      const response = await fetch(`http://localhost:3000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create relationship');
      }

      return response.json();
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['relationships']);
        refetchTaskSemantic();
        refetchSemanticPrimitive();
        setShowCreateForm(false);
        setFormData({ weight: 1.0, order_index: 0, is_required: true });
        setFormErrors('');
      },
      onError: (error: Error) => {
        setFormErrors(error.message);
      }
    }
  );

  // Delete relationship mutation
  const deleteRelationMutation = useMutation(
    async (relationship: Relationship) => {
      const endpoint = relationship.task_rule_id 
        ? '/api/v1/relationships/task-semantic'
        : '/api/v1/relationships/semantic-primitive';

      const body = relationship.task_rule_id ? {
        task_rule_id: relationship.task_rule_id,
        semantic_rule_id: relationship.semantic_rule_id
      } : {
        semantic_rule_id: relationship.semantic_rule_id,
        primitive_rule_id: relationship.primitive_rule_id
      };

      const response = await fetch(`http://localhost:3000${endpoint}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete relationship');
      }

      return response.json();
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['relationships']);
        refetchTaskSemantic();
        refetchSemanticPrimitive();
      }
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormErrors('');

    if (activeTab === 'task_semantic') {
      if (!formData.task_rule_id || !formData.semantic_rule_id) {
        setFormErrors('Both task rule and semantic rule are required');
        return;
      }
    } else {
      if (!formData.semantic_rule_id || !formData.primitive_rule_id) {
        setFormErrors('Both semantic rule and primitive rule are required');
        return;
      }
    }

    createRelationMutation.mutate(formData);
  };

  const handleDelete = (relationship: Relationship) => {
    const relationshipType = relationship.task_rule_id ? 'task-semantic' : 'semantic-primitive';
    const relationshipName = relationship.task_rule_id 
      ? `${relationship.task_name} → ${relationship.semantic_name}`
      : `${relationship.semantic_name} → ${relationship.primitive_name}`;

    if (window.confirm(`Are you sure you want to delete the ${relationshipType} relationship: ${relationshipName}?`)) {
      deleteRelationMutation.mutate(relationship);
    }
  };

  const resetForm = () => {
    setFormData({ weight: 1.0, order_index: 0, is_required: true });
    setFormErrors('');
    setShowCreateForm(false);
  };

  const resetFilters = () => {
    setSearchTerm('');
    setFilterRequired('all');
    setSortBy('name');
    setSortOrder('asc');
  };

  // Get weight color based on weight value
  const getWeightColor = (weight: number) => {
    if (weight >= 0.8) return 'text-green-600 bg-green-50';
    if (weight >= 0.5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  // Reset filters when switching tabs
  useEffect(() => {
    resetFilters();
  }, [activeTab]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Escape to clear search
      if (event.key === 'Escape' && searchTerm) {
        setSearchTerm('');
      }
      // Ctrl/Cmd + K to focus search
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[placeholder="Search relationships..."]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [searchTerm]);

  const rawRelations = activeTab === 'task_semantic' ? taskSemanticRelations : semanticPrimitiveRelations;
  const isLoading = rulesLoading || (activeTab === 'task_semantic' ? taskSemanticLoading : semanticPrimitiveLoading);

  // Filter and sort relationships
  const filteredAndSortedRelations = React.useMemo(() => {
    if (!rawRelations) return [];

    let filtered = rawRelations.filter((relation: Relationship) => {
      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const taskName = relation.task_name?.toLowerCase() || '';
        const semanticName = relation.semantic_name?.toLowerCase() || '';
        const primitiveName = relation.primitive_name?.toLowerCase() || '';
        
        const matchesSearch = taskName.includes(searchLower) ||
                            semanticName.includes(searchLower) ||
                            primitiveName.includes(searchLower);
        
        if (!matchesSearch) return false;
      }

      // Required filter
      if (filterRequired !== 'all') {
        const isRequired = relation.is_required;
        if (filterRequired === 'required' && !isRequired) return false;
        if (filterRequired === 'optional' && isRequired) return false;
      }

      return true;
    });

    // Sort
    filtered.sort((a: Relationship, b: Relationship) => {
      let aVal, bVal;

      switch (sortBy) {
        case 'weight':
          aVal = a.weight;
          bVal = b.weight;
          break;
        case 'order':
          aVal = a.order_index;
          bVal = b.order_index;
          break;
        case 'name':
        default:
          if (activeTab === 'task_semantic') {
            aVal = a.task_name?.toLowerCase() || '';
            bVal = b.task_name?.toLowerCase() || '';
          } else {
            aVal = a.semantic_name?.toLowerCase() || '';
            bVal = b.semantic_name?.toLowerCase() || '';
          }
          break;
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      } else {
        return sortOrder === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
      }
    });

    return filtered;
  }, [rawRelations, searchTerm, filterRequired, sortBy, sortOrder, activeTab]);

  // Calculate statistics
  const stats = {
    taskSemanticCount: taskSemanticRelations?.length || 0,
    semanticPrimitiveCount: semanticPrimitiveRelations?.length || 0,
    totalTaskRules: taskRules.length,
    totalSemanticRules: semanticRules.length,
    totalPrimitiveRules: primitiveRules.length,
    filteredCount: filteredAndSortedRelations.length
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="page-header mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Rule Relationships</h1>
          <p className="text-gray-600">
            Manage relationships between task and semantic rules, and between semantic and primitive rules
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Create Relationship
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="text-sm font-medium text-gray-500">Task Rules</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalTaskRules}</div>
        </div>
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="text-sm font-medium text-gray-500">Semantic Rules</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalSemanticRules}</div>
        </div>
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="text-sm font-medium text-gray-500">Primitive Rules</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalPrimitiveRules}</div>
        </div>
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="text-sm font-medium text-gray-500">Task → Semantic</div>
          <div className="text-2xl font-bold text-green-600">{stats.taskSemanticCount}</div>
        </div>
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="text-sm font-medium text-gray-500">Semantic → Primitive</div>
          <div className="text-2xl font-bold text-blue-600">{stats.semanticPrimitiveCount}</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white shadow-sm rounded-lg mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab('task_semantic')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'task_semantic'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Task → Semantic
              {taskSemanticRelations && (
                <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
                  {taskSemanticRelations.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('semantic_primitive')}
              className={`py-4 px-6 border-b-2 font-medium text-sm ${
                activeTab === 'semantic_primitive'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Semantic → Primitive
              {semanticPrimitiveRelations && (
                <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs">
                  {semanticPrimitiveRelations.length}
                </span>
              )}
            </button>
          </nav>
        </div>
      </div>

      {/* Create Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Create {activeTab === 'task_semantic' ? 'Task → Semantic' : 'Semantic → Primitive'} Relationship
              </h3>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {activeTab === 'task_semantic' ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Task Rule
                      </label>
                      <select
                        value={formData.task_rule_id || ''}
                        onChange={(e) => setFormData({...formData, task_rule_id: parseInt(e.target.value)})}
                        className="input-field"
                        required
                      >
                        <option value="">Select a task rule</option>
                        {taskRules.map(rule => (
                          <option key={rule.id} value={rule.id}>
                            {rule.name} (ID: {rule.id})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Semantic Rule
                      </label>
                      <select
                        value={formData.semantic_rule_id || ''}
                        onChange={(e) => setFormData({...formData, semantic_rule_id: parseInt(e.target.value)})}
                        className="input-field"
                        required
                      >
                        <option value="">Select a semantic rule</option>
                        {semanticRules.map(rule => (
                          <option key={rule.id} value={rule.id}>
                            {rule.name} (ID: {rule.id})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Context Override (JSON, optional)
                      </label>
                      <textarea
                        value={formData.context_override || ''}
                        onChange={(e) => setFormData({...formData, context_override: e.target.value})}
                        placeholder='{"key": "value"}'
                        rows={3}
                        className="input-field font-mono text-sm"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Semantic Rule
                      </label>
                      <select
                        value={formData.semantic_rule_id || ''}
                        onChange={(e) => setFormData({...formData, semantic_rule_id: parseInt(e.target.value)})}
                        className="input-field"
                        required
                      >
                        <option value="">Select a semantic rule</option>
                        {semanticRules.map(rule => (
                          <option key={rule.id} value={rule.id}>
                            {rule.name} (ID: {rule.id})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Primitive Rule
                      </label>
                      <select
                        value={formData.primitive_rule_id || ''}
                        onChange={(e) => setFormData({...formData, primitive_rule_id: parseInt(e.target.value)})}
                        className="input-field"
                        required
                      >
                        <option value="">Select a primitive rule</option>
                        {primitiveRules.map(rule => (
                          <option key={rule.id} value={rule.id}>
                            {rule.name} (ID: {rule.id})
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Weight
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.weight}
                      onChange={(e) => setFormData({...formData, weight: parseFloat(e.target.value)})}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Order
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.order_index}
                      onChange={(e) => setFormData({...formData, order_index: parseInt(e.target.value)})}
                      className="input-field"
                    />
                  </div>
                </div>

                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_required}
                      onChange={(e) => setFormData({...formData, is_required: e.target.checked})}
                      className="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-700">Required relationship</span>
                  </label>
                </div>

                {formErrors && (
                  <div className="text-red-600 text-sm flex items-center">
                    <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                    {formErrors}
                  </div>
                )}

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={resetForm}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createRelationMutation.isLoading}
                    className="btn-primary"
                  >
                    {createRelationMutation.isLoading ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Filter and Search Controls */}
      <div className="bg-white shadow-sm rounded-lg p-6 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search relationships... (Ctrl+K)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  title="Clear search (Esc)"
                >
                  ×
                </button>
              )}
            </div>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-4">
            {/* Required Filter */}
            <div className="flex items-center gap-2">
              <FunnelIcon className="h-4 w-4 text-gray-500" />
              <select
                value={filterRequired}
                onChange={(e) => setFilterRequired(e.target.value as any)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">All Relationships</option>
                <option value="required">Required Only</option>
                <option value="optional">Optional Only</option>
              </select>
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <ArrowsUpDownIcon className="h-4 w-4 text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="name">Sort by Name</option>
                <option value="weight">Sort by Weight</option>
                <option value="order">Sort by Order</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
              >
                <ArrowsUpDownIcon className={`h-4 w-4 ${sortOrder === 'desc' ? 'rotate-180' : ''} transition-transform`} />
              </button>
            </div>

            {/* Clear Filters */}
            {(searchTerm || filterRequired !== 'all' || sortBy !== 'name' || sortOrder !== 'asc') && (
              <button
                onClick={resetFilters}
                className="text-sm text-gray-600 hover:text-gray-800 underline"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Results Count */}
        <div className="mt-4 text-sm text-gray-600">
          Showing {stats.filteredCount} of {activeTab === 'task_semantic' ? stats.taskSemanticCount : stats.semanticPrimitiveCount} relationships
        </div>
      </div>

      {/* Relationships List */}
      <div className="bg-white shadow-sm rounded-lg">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="spinner w-6 h-6" />
          </div>
        ) : filteredAndSortedRelations && filteredAndSortedRelations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Relationship
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weight
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Required
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedRelations.map((relation: Relationship, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-gray-900">
                          {activeTab === 'task_semantic' ? relation.task_name : relation.semantic_name}
                        </div>
                        <ArrowRightIcon className="h-4 w-4 mx-2 text-gray-400" />
                        <div className="text-sm text-gray-900">
                          {activeTab === 'task_semantic' ? relation.semantic_name : relation.primitive_name}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getWeightColor(relation.weight)}`}>
                          {relation.weight}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {relation.order_index}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        relation.is_required 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {relation.is_required ? 'Required' : 'Optional'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDelete(relation)}
                        disabled={deleteRelationMutation.isLoading}
                        className="text-red-600 hover:text-red-900 transition-colors disabled:opacity-50"
                        title="Delete Relationship"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            {rawRelations && rawRelations.length > 0 ? (
              // Has relationships but none match filters
              <>
                <MagnifyingGlassIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No relationships found
                </h3>
                <p className="text-gray-500 mb-4">
                  Try adjusting your search terms or filters to find relationships.
                </p>
                <button
                  onClick={resetFilters}
                  className="btn-secondary"
                >
                  Clear All Filters
                </button>
              </>
            ) : (
              // No relationships at all
              <>
                <ArrowRightIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No {activeTab === 'task_semantic' ? 'task-semantic' : 'semantic-primitive'} relationships
                </h3>
                <p className="text-gray-500 mb-4">
                  Create relationships to connect rules and build your prompt hierarchy.
                </p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="btn-primary"
                >
                  Create First Relationship
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Relationships;