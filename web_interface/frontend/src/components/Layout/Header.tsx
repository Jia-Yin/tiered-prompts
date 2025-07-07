import React from 'react';
import { Bars3Icon, BellIcon } from '@heroicons/react/24/outline';
import { useWebSocket } from '../../contexts/WebSocketContext';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { isConnected, lastMessage } = useWebSocket();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between h-16 px-4">
        {/* Left side */}
        <div className="flex items-center">
          <button
            className="lg:hidden p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100"
            onClick={onMenuClick}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          
          <div className="hidden lg:block ml-4">
            <h2 className="text-lg font-semibold text-gray-900">
              AI Prompt Engineering System
            </h2>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* WebSocket status indicator */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="hidden sm:inline text-sm text-gray-600">
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>

          {/* Notifications */}
          <button className="p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100 relative">
            <BellIcon className="h-6 w-6" />
            {lastMessage && (
              <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white" />
            )}
          </button>

          {/* User menu */}
          <div className="flex items-center">
            <div className="ml-3">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                    <span className="text-white text-sm font-medium">AI</span>
                  </div>
                </div>
                <div className="ml-3 hidden sm:block">
                  <div className="text-sm font-medium text-gray-700">AI Assistant</div>
                  <div className="text-xs text-gray-500">System Admin</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;