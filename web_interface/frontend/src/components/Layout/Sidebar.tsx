import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  DocumentTextIcon, 
  BeakerIcon, 
  ChartBarIcon,
  ArrowRightIcon,
  CogIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useWebSocket } from '../../contexts/WebSocketContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Rules', href: '/rules', icon: DocumentTextIcon },
  { name: 'Playground', href: '/playground', icon: BeakerIcon },
  { name: 'Relationships', href: '/relationships', icon: ArrowRightIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { isConnected, connectionStatus } = useWebSocket();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden bg-gray-600 bg-opacity-75"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-4 bg-primary-600">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-primary-600 font-bold text-lg">AI</span>
              </div>
            </div>
            <div className="ml-3">
              <h1 className="text-white font-semibold text-lg">Prompt System</h1>
            </div>
          </div>
          
          {/* Close button for mobile */}
          <button
            className="lg:hidden text-white hover:text-gray-200"
            onClick={onClose}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Connection status */}
        <div className="px-4 py-3 border-b border-gray-200">
          <div className="flex items-center">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              connectionStatus === 'connected' ? 'bg-green-500' : 
              connectionStatus === 'connecting' ? 'bg-yellow-500' : 
              'bg-red-500'
            }`} />
            <span className="text-sm text-gray-600">
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'connecting' ? 'Connecting...' : 
               'Disconnected'}
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/' && location.pathname.startsWith(item.href));
            
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={onClose}
                className={`
                  group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200
                  ${isActive 
                    ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-600' 
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                <item.icon 
                  className={`mr-3 flex-shrink-0 h-5 w-5 ${
                    isActive ? 'text-primary-600' : 'text-gray-500 group-hover:text-gray-600'
                  }`} 
                />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <div>AI Prompt Engineering System</div>
            <div>Version 1.0.0</div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;