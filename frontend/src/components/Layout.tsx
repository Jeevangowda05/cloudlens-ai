import React, { ReactNode, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLocation, Link } from 'react-router-dom';
import {
  LogOut,
  Menu,
  X,
  LayoutDashboard,
  Cloud,
  BarChart3,
  Lightbulb,
  Bell,
  Sliders,
  MessageCircle,
  Leaf,
  FlaskConical,
  MapPin,
  AlertTriangle,
  TrendingUp,
  FileText,
  Tag,
} from 'lucide-react';
import { ChatBox } from './ChatBox';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
  };

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/clouds', label: 'Clouds', icon: Cloud },
    { path: '/billing', label: 'Billing', icon: BarChart3 },
    { path: '/recommendations', label: 'Recommendations', icon: Lightbulb },
    { path: '/carbon', label: 'Carbon', icon: Leaf },
    { path: '/simulator', label: 'Simulator', icon: FlaskConical },
    { path: '/regions', label: 'Regions', icon: MapPin },
    { path: '/idle-resources', label: 'Idle Resources', icon: AlertTriangle },
    { path: '/forecast', label: 'Forecast', icon: TrendingUp },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/tags', label: 'Tags', icon: Tag },
    { path: '/anomalies', label: 'Anomalies', icon: Bell },
    { path: '/alerts', label: 'Alerts', icon: Bell },
    { path: '/settings', label: 'Settings', icon: Sliders },
  ];

  const NavLink = ({ path, label, icon: Icon }: any) => (
    <Link
      to={path}
      onClick={() => setIsMenuOpen(false)}
      className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition ${
        isActive(path)
          ? 'bg-primary text-white'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <Icon size={18} />
      <span>{label}</span>
    </Link>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center flex-shrink-0">
              <h1 className="text-2xl font-bold text-primary">☁️ CloudLens AI</h1>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navItems.map((item) => (
                <NavLink key={item.path} {...item} />
              ))}
            </nav>

            {/* Desktop Right Section */}
            <div className="hidden lg:flex items-center space-x-4">
              <span className="text-gray-700 text-sm">{user?.email}</span>
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="flex items-center space-x-2 bg-blue-50 text-primary px-3 py-2 rounded-lg hover:bg-blue-100 transition"
                title="Open CloudLens AI Chat"
              >
                <MessageCircle size={18} />
                <span className="text-sm">Ask AI</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
              >
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <nav className="lg:hidden border-t border-gray-200 py-4 space-y-2">
              {navItems.map((item) => (
                <NavLink key={item.path} {...item} />
              ))}
              
              <div className="border-t border-gray-200 pt-4 mt-4 space-y-2">
                <div className="px-3 py-2 text-gray-700 text-sm">
                  {user?.email}
                </div>
                <button
                  onClick={() => setChatOpen(!chatOpen)}
                  className="w-full flex items-center space-x-2 bg-blue-50 text-primary px-3 py-2 rounded-lg hover:bg-blue-100 transition"
                >
                  <MessageCircle size={18} />
                  <span>Ask AI</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-2 bg-red-500 text-white px-3 py-2 rounded-lg hover:bg-red-600 transition"
                >
                  <LogOut size={18} />
                  <span>Logout</span>
                </button>
              </div>
            </nav>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Floating Chat Button - Always Available */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 bg-primary text-white p-4 rounded-full shadow-lg hover:bg-blue-600 transition z-30"
          title="Open CloudLens AI Chat"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat Box - Available on All Pages */}
      <ChatBox isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  );
};
