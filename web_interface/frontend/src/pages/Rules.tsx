import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  FunnelIcon,
  Squares2X2Icon,
  ListBulletIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import { listRules, searchRules } from '../services/api';
import { Rule, SearchRulesRequest } from '../types';
import RuleCard from '../components/Rules/RuleCard';
import RuleTable from '../components/Rules/RuleTable';

const Rules: React.FC = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filterType, setFilterType] = useState<'all' | 'primitive' | 'semantic' | 'task'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Rule[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Fetch all rules (always fetch all, filter on frontend)
  const { data: rawRules, isLoading, refetch } = useQuery(
    ['rules'],
    () => listRules(), // Always fetch all rules
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  // Ensure allRules is always an array
  const allRules = React.useMemo(() => {
    if (!rawRules) return [];
    
    // Handle array response (when no filter is applied)
    if (Array.isArray(rawRules)) return rawRules;
    
    // Handle object response with rules array (when filtering by type)
    if (rawRules && typeof rawRules === 'object' && 'rules' in rawRules && Array.isArray((rawRules as any).rules)) {
      return (rawRules as any).rules;
    }
    
    // Handle unexpected data format
    console.warn('Expected array or {rules: []} from listRules, got:', typeof rawRules, rawRules);
    return [];
  }, [rawRules]);

  // Handle search
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const searchRequest: SearchRulesRequest = {
        query: query.trim(),
        search_type: 'content',
        rule_type: filterType !== 'all' ? filterType : 'all',
        limit: 20,
      };

      const response = await searchRules(searchRequest);
      const results: Rule[] = response.results.map(result => ({
        id: result.rule_id, // Keep original numeric ID
        name: result.name,
        type: result.type as 'primitive' | 'semantic' | 'task',
        content: result.content,
      }));
      
      setSearchResults(results);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Debounced search
  React.useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, filterType]);

  // Apply frontend filtering and search
  const displayRules = React.useMemo(() => {
    let rules = allRules;
    
    // Apply type filter
    if (filterType !== 'all') {
      rules = rules.filter((rule: Rule) => rule.type === filterType);
    }
    
    // Apply search results if searching
    if (searchQuery.trim()) {
      return searchResults;
    }
    
    return rules;
  }, [allRules, filterType, searchQuery, searchResults]);

  const ruleTypeStats = React.useMemo(() => {
    if (!Array.isArray(allRules) || allRules.length === 0) {
      return { total: 0, primitive: 0, semantic: 0, task: 0 };
    }
    
    return allRules.reduce((acc, rule) => {
      if (rule && rule.type) {
        acc[rule.type] = (acc[rule.type] || 0) + 1;
        acc.total = (acc.total || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);
  }, [allRules]);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Rules</h1>
          <p className="text-gray-600">
            Manage your hierarchical rule system ({ruleTypeStats.total || 0} total rules)
          </p>
        </div>
        <div className="flex space-x-3">
          <Link
            to="/rules/new"
            className="btn-primary inline-flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Rule
          </Link>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search rules..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input-field pl-10"
            />
            {isSearching && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="spinner" />
              </div>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center">
            <FunnelIcon className="h-5 w-5 text-gray-400 mr-2" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as any)}
              className="input-field"
            >
              <option value="all">All Types ({ruleTypeStats.total || 0})</option>
              <option value="primitive">Primitive ({ruleTypeStats.primitive || 0})</option>
              <option value="semantic">Semantic ({ruleTypeStats.semantic || 0})</option>
              <option value="task">Task ({ruleTypeStats.task || 0})</option>
            </select>
          </div>

          {/* View mode toggle */}
          <div className="flex border border-gray-300 rounded-md">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 ${
                viewMode === 'grid'
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Squares2X2Icon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 border-l border-gray-300 ${
                viewMode === 'list'
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <ListBulletIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Search results indicator */}
      {searchQuery.trim() && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex items-center">
            <MagnifyingGlassIcon className="h-5 w-5 text-blue-400 mr-2" />
            <span className="text-sm text-blue-700">
              Showing {displayRules.length} search results for "{searchQuery}"
            </span>
            <button
              onClick={() => setSearchQuery('')}
              className="ml-auto text-sm text-blue-600 hover:text-blue-800"
            >
              Clear search
            </button>
          </div>
        </div>
      )}

      {/* Rules content */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="spinner w-8 h-8 mx-auto mb-4" />
            <div className="text-gray-500">Loading rules...</div>
          </div>
        </div>
      ) : displayRules.length === 0 ? (
        <div className="text-center py-12">
          <ShareIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {searchQuery.trim() ? 'No search results' : 'No rules found'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery.trim() 
              ? 'Try adjusting your search terms or filters.'
              : 'Get started by creating your first rule.'
            }
          </p>
          {!searchQuery.trim() && (
            <div className="mt-6">
              <Link to="/rules/new" className="btn-primary">
                <PlusIcon className="h-5 w-5 mr-2" />
                Create Rule
              </Link>
            </div>
          )}
        </div>
      ) : (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayRules.map((rule: Rule) => (
                <RuleCard 
                  key={`${rule.type}-${rule.id}`} 
                  rule={rule} 
                  onUpdate={refetch}
                />
              ))}
            </div>
          ) : (
            <RuleTable 
              rules={displayRules} 
              onUpdate={refetch}
            />
          )}
        </>
      )}
    </div>
  );
};

export default Rules;