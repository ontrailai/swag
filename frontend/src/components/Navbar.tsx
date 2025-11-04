import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, Settings, History } from 'lucide-react';
import { motion } from 'framer-motion';
import swagLogo from '../assets/swag-logo.svg';

export const Navbar: React.FC = () => {
  const [isOnline, setIsOnline] = useState(true);

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        setIsOnline(response.ok);
      } catch {
        setIsOnline(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload', label: 'Invoices', icon: Upload },
    { to: '/history', label: 'History', icon: History },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="sidebar">
      {/* Logo Section */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-4">
          <motion.div
            className="relative"
            animate={{
              filter: [
                'drop-shadow(0 0 8px rgba(50,255,106,0.6))',
                'drop-shadow(0 0 12px rgba(255,60,241,0.6))',
                'drop-shadow(0 0 8px rgba(50,255,106,0.6))'
              ]
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <img
              src={swagLogo}
              alt="Swag Golf Logo"
              className="w-14 h-14"
            />
          </motion.div>
          <div>
            <h1 className="text-xl font-display font-black uppercase tracking-wider bg-gradient-to-r from-swag-neon-green to-swag-gold bg-clip-text text-transparent leading-tight">
              SWAG
            </h1>
            <p className="text-xs font-body text-swag-skull-white/70 tracking-wide">
              Pricing Intelligence
            </p>
          </div>
        </div>
      </motion.div>

      {/* Status Indicator */}
      <motion.div
        className="mb-6 px-4 py-3 rounded-xl bg-gradient-to-r from-swag-dark-tertiary to-swag-dark-secondary border border-swag-neon-green/20"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center gap-3">
          <motion.div
            className={`w-3 h-3 rounded-full ${
              isOnline ? 'bg-swag-neon-green' : 'bg-red-500'
            }`}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.8, 1, 0.8]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <div>
            <p className="text-xs font-semibold text-swag-skull-white">
              {isOnline ? 'System Online' : 'System Offline'}
            </p>
            <p className="text-xs text-swag-skull-white/50">
              {isOnline ? 'Ready to process' : 'Connecting...'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Navigation Links */}
      <nav className="space-y-2">
        {links.map((link, index) => {
          const Icon = link.icon;
          return (
            <motion.div
              key={link.to}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
            >
              <NavLink
                to={link.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="font-semibold tracking-wide">{link.label}</span>
              </NavLink>
            </motion.div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-auto pt-6 border-t border-swag-neon-green/20">
        <div className="text-center space-y-1">
          <p className="text-xs font-display font-bold text-swag-gold uppercase tracking-wider">
            v2.0.0
          </p>
          <p className="text-xs text-swag-skull-white/50">
            Production Ready
          </p>
        </div>
      </div>
    </div>
  );
};
