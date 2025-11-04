import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, Settings, History, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

export const Sidebar: React.FC = () => {
  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload', label: 'Upload & Process', icon: Upload },
    { to: '/history', label: 'History', icon: History },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="sidebar">
      {/* Logo */}
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3">
          <Zap className="w-10 h-10 text-swag-neon-green" />
          <div>
            <h1 className="text-xl font-black text-transparent bg-gradient-to-r from-swag-neon-green to-swag-neon-blue bg-clip-text">
              SWAG PRICING
            </h1>
            <p className="text-xs text-swag-gold">INTELLIGENCE TOOL</p>
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
              transition={{ delay: index * 0.1 }}
            >
              <NavLink
                to={link.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="font-semibold">{link.label}</span>
              </NavLink>
            </motion.div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-auto pt-6 border-t border-swag-neon-green/20">
        <p className="text-xs text-swag-skull-white/50 text-center">
          v2.0.0 • LOCAL DEPLOY
        </p>
        <p className="text-xs text-swag-gold/70 text-center mt-1">
          PHASE 5: REACT MIGRATION
        </p>
      </div>
    </div>
  );
};
