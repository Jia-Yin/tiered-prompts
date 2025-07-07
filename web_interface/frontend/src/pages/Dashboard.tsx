import React from 'react';
import { useQuery } from 'react-query';
import { 
  DocumentTextIcon, 
  CpuChipIcon, 
  ChartBarIcon, 
  ClockIcon 
} from '@heroicons/react/24/outline';
import { getSystemStatus, getPerformanceStats, listRules } from '../services/api';
import { useWebSocket } from '../contexts/WebSocketContext';

const Dashboard: React.FC = () => {
  const { lastMessage, isConnected } = useWebSocket();

  // Fetch dashboard data
  const { data: systemStatus } = useQuery('systemStatus', getSystemStatus, {
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: performanceStats } = useQuery('performanceStats', getPerformanceStats, {
    refetchInterval: 60000, // Refetch every minute
  });

  const { data: rules } = useQuery('rules', () => listRules(), {
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  // Calculate rule type counts
  const ruleStats = React.useMemo(() => {
    if (!rules) return { primitive: 0, semantic: 0, task: 0, total: 0 };
    
    return rules.reduce((acc, rule) => {
      acc[rule.type]++;
      acc.total++;
      return acc;
    }, { primitive: 0, semantic: 0, task: 0, total: 0 });
  }, [rules]);

  const stats = [
    {
      name: 'Total Rules',
      value: ruleStats.total,
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
      change: '+2.1%',
      changeType: 'positive' as const,
    },
    {
      name: 'MCP Server',
      value: systemStatus?.mcp_server === 'connected' ? 'Online' : 'Offline',
      icon: CpuChipIcon,
      color: systemStatus?.mcp_server === 'connected' ? 'bg-green-500' : 'bg-red-500',
      change: isConnected ? 'Connected' : 'Disconnected',
      changeType: isConnected ? 'positive' : 'negative' as const,
    },
    {
      name: 'Cache Hit Rate',
      value: performanceStats?.system_stats?.cache_hit_rate 
        ? `${(performanceStats.system_stats.cache_hit_rate * 100).toFixed(1)}%`
        : 'N/A',
      icon: ChartBarIcon,
      color: 'bg-purple-500',
      change: '+5.4%',
      changeType: 'positive' as const,
    },
    {
      name: 'Avg Response Time',
      value: performanceStats?.system_stats?.average_generation_time 
        ? `${(performanceStats.system_stats.average_generation_time * 1000).toFixed(0)}ms`
        : 'N/A',
      icon: ClockIcon,
      color: 'bg-orange-500',
      change: '-2.3%',
      changeType: 'positive' as const,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to the AI Prompt Engineering System</p>
        </div>
      </div>

      {/* WebSocket status alert */}
      {lastMessage && lastMessage.type === 'connection_established' && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">
                Real-time Connection Established
              </h3>
              <div className="mt-1 text-sm text-green-700">
                {lastMessage.message}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`w-8 h-8 rounded-md ${stat.color} flex items-center justify-center`}>
                  <stat.icon className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </div>
                    <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Rule breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rule Distribution</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Primitive Rules</span>
              <div className="flex items-center">
                <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${ruleStats.total > 0 ? (ruleStats.primitive / ruleStats.total) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900">{ruleStats.primitive}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Semantic Rules</span>
              <div className="flex items-center">
                <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${ruleStats.total > 0 ? (ruleStats.semantic / ruleStats.total) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900">{ruleStats.semantic}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Task Rules</span>
              <div className="flex items-center">
                <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${ruleStats.total > 0 ? (ruleStats.task / ruleStats.total) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-gray-900">{ruleStats.task}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Performance</h3>
          {performanceStats ? (
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Prompts Generated</span>
                <span className="text-sm font-medium text-gray-900">
                  {performanceStats.system_stats.total_prompts_generated?.toLocaleString() || 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">System Uptime</span>
                <span className="text-sm font-medium text-gray-900">
                  {performanceStats.system_stats.uptime_hours 
                    ? `${performanceStats.system_stats.uptime_hours.toFixed(1)}h`
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Memory Usage</span>
                <span className="text-sm font-medium text-gray-900">
                  {performanceStats.performance_metrics?.memory_usage_mb 
                    ? `${performanceStats.performance_metrics.memory_usage_mb.toFixed(1)} MB`
                    : 'N/A'}
                </span>
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-500">Loading performance data...</div>
          )}
        </div>
      </div>

      {/* Recent activity */}
      {lastMessage && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="bg-gray-50 rounded-md p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900">
                  {lastMessage.type === 'mcp_operation' && `MCP Operation: ${lastMessage.operation}`}
                  {lastMessage.type === 'rule_update' && `Rule ${lastMessage.action}: ${lastMessage.rule_type}`}
                  {lastMessage.type === 'system_status' && 'System Status Update'}
                  {lastMessage.type === 'connection_established' && 'WebSocket Connected'}
                </div>
                {lastMessage.message && (
                  <div className="text-sm text-gray-600 mt-1">{lastMessage.message}</div>
                )}
              </div>
              <div className="text-xs text-gray-500">
                {new Date(lastMessage.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;