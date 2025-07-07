import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useLocation } from 'react-router-dom';
import {
  PlayIcon,
  ClipboardDocumentIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { listRules, generatePrompt, handleApiError } from '../services/api';
import { Rule, GeneratePromptRequest, PromptResult } from '../types';

const Playground: React.FC = () => {
  const location = useLocation();
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null);
  const [context, setContext] = useState<Record<string, string>>({});
  const [contextInput, setContextInput] = useState('');
  const [targetModel, setTargetModel] = useState<'claude' | 'gpt' | 'gemini'>('claude');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPrompt, setGeneratedPrompt] = useState<PromptResult | null>(null);
  const [error, setError] = useState<string>('');

  // Fetch rules (only semantic and task rules)
  const { data: rawRules, isLoading } = useQuery(
    ['rules'],
    () => listRules(),
    {
      select: (rules) => rules.filter(rule => rule.type === 'semantic' || rule.type === 'task')
    }
  );

  const rules = rawRules || [];

  // Handle pre-selected rule from navigation state
  useEffect(() => {
    const state = location.state as { selectedRule?: Rule };
    if (state?.selectedRule && (state.selectedRule.type === 'semantic' || state.selectedRule.type === 'task')) {
      setSelectedRule(state.selectedRule);
      // Set default context based on rule type
      if (state.selectedRule.type === 'semantic') {
        const defaultContext = { "tone": "professional", "context": "code review", "audience": "developers" };
        setContext(defaultContext);
        setContextInput(JSON.stringify(defaultContext, null, 2));
      } else if (state.selectedRule.type === 'task') {
        const defaultContext = { "component": "UserProfile", "criteria": "performance and accessibility", "language": "TypeScript", "framework": "React" };
        setContext(defaultContext);
        setContextInput(JSON.stringify(defaultContext, null, 2));
      }
    }
  }, [location.state]);

  // Parse context input (JSON format)
  const handleContextChange = (value: string) => {
    setContextInput(value);
    try {
      if (value.trim()) {
        const parsed = JSON.parse(value);
        setContext(parsed);
        setError('');
      } else {
        setContext({});
        setError('');
      }
    } catch (e) {
      setError('Invalid JSON format in context');
    }
  };

  // Generate prompt
  const handleGeneratePrompt = async () => {
    if (!selectedRule) {
      setError('Please select a rule first');
      return;
    }

    setIsGenerating(true);
    setError('');

    try {
      const request: GeneratePromptRequest = {
        rule_name: selectedRule.name,
        context: context,
        target_model: targetModel
      };

      const result = await generatePrompt(request);
      setGeneratedPrompt(result);
    } catch (err) {
      console.error('Error generating prompt:', err);
      setError(handleApiError(err));
    } finally {
      setIsGenerating(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  // Get placeholder context based on rule type
  const getContextPlaceholder = () => {
    if (!selectedRule) return '{}';
    
    if (selectedRule.type === 'semantic') {
      return JSON.stringify({
        "tone": "professional",
        "context": "code review",
        "audience": "developers"
      }, null, 2);
    } else if (selectedRule.type === 'task') {
      return JSON.stringify({
        "component": "UserProfile",
        "criteria": "performance and accessibility",
        "language": "TypeScript",
        "framework": "React"
      }, null, 2);
    }
    return '{}';
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="page-header mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Prompt Playground</h1>
          <p className="text-gray-600">
            Generate prompts from semantic and task rules with custom context
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel - Configuration */}
        <div className="space-y-6">
          {/* Rule Selection */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Rule</h2>
            
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="spinner w-6 h-6" />
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {rules.map((rule) => (
                  <div
                    key={`${rule.type}-${rule.id}`}
                    onClick={() => setSelectedRule(rule)}
                    className={`p-3 rounded-md border cursor-pointer transition-colors ${
                      selectedRule?.id === rule.id && selectedRule?.type === rule.type
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900">{rule.name}</div>
                        <div className="text-sm text-gray-500">{rule.description}</div>
                      </div>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        rule.type === 'semantic' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-purple-100 text-purple-800'
                      }`}>
                        {rule.type}
                      </span>
                    </div>
                  </div>
                ))}
                
                {rules.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    No semantic or task rules found
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Context Input */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Context Variables</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-2">
                  Context (JSON format)
                </label>
                <textarea
                  id="context"
                  value={contextInput}
                  onChange={(e) => handleContextChange(e.target.value)}
                  placeholder={getContextPlaceholder()}
                  rows={8}
                  className="input-field font-mono text-sm"
                />
                {error && (
                  <p className="mt-2 text-sm text-red-600 flex items-center">
                    <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                    {error}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="target_model" className="block text-sm font-medium text-gray-700 mb-2">
                  Target Model
                </label>
                <select
                  id="target_model"
                  value={targetModel}
                  onChange={(e) => setTargetModel(e.target.value as any)}
                  className="input-field"
                >
                  <option value="claude">Claude</option>
                  <option value="gpt">GPT</option>
                  <option value="gemini">Gemini</option>
                </select>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGeneratePrompt}
            disabled={!selectedRule || isGenerating || !!error}
            className="w-full btn-primary flex items-center justify-center"
          >
            {isGenerating ? (
              <>
                <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <PlayIcon className="h-5 w-5 mr-2" />
                Generate Prompt
              </>
            )}
          </button>
        </div>

        {/* Right Panel - Generated Prompt */}
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Generated Prompt</h2>
            {generatedPrompt && (
              <button
                onClick={() => copyToClipboard(generatedPrompt.prompt)}
                className="btn-secondary flex items-center"
              >
                <ClipboardDocumentIcon className="h-4 w-4 mr-2" />
                Copy
              </button>
            )}
          </div>

          {generatedPrompt ? (
            <div className="space-y-4">
              {/* Prompt Content */}
              <div>
                <div className="bg-gray-50 rounded-md p-4 border">
                  <pre className="whitespace-pre-wrap text-sm text-gray-900 font-mono">
                    {generatedPrompt.prompt}
                  </pre>
                </div>
              </div>

              {/* Metadata */}
              <div className="border-t pt-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Metadata</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Rule:</span>
                    <span className="ml-2 text-gray-900">{generatedPrompt.metadata.rule_name}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Model:</span>
                    <span className="ml-2 text-gray-900">{generatedPrompt.metadata.target_model}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Generation Time:</span>
                    <span className="ml-2 text-gray-900">{generatedPrompt.metadata.generation_time}s</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Context Variables:</span>
                    <span className="ml-2 text-gray-900">{generatedPrompt.metadata.context_variables.join(', ') || 'None'}</span>
                  </div>
                </div>

                {generatedPrompt.metadata.rules_used && (
                  <div className="mt-2">
                    <span className="text-gray-500">Rules Used:</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {generatedPrompt.metadata.rules_used.map((rule, index) => (
                        <span key={index} className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-700">
                          {rule}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              <div className="text-center">
                <PlayIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Select a rule and click "Generate Prompt" to see the result</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Playground;