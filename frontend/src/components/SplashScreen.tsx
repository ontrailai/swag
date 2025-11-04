import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import swagLogo from '../assets/swag-logo.svg';

interface SplashScreenProps {
  onComplete: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onComplete, 500);
    }, 2500);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-swag-dark"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex flex-col items-center gap-8">
            {/* Logo with pulse animation */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{
                scale: [0.8, 1.05, 1],
                opacity: 1
              }}
              transition={{
                duration: 1.2,
                times: [0, 0.6, 1],
                ease: "easeOut"
              }}
              className="relative"
            >
              {/* Glow effect */}
              <motion.div
                className="absolute inset-0 rounded-full blur-3xl"
                animate={{
                  background: [
                    'radial-gradient(circle, rgba(50,255,106,0.4) 0%, transparent 70%)',
                    'radial-gradient(circle, rgba(255,60,241,0.4) 0%, transparent 70%)',
                    'radial-gradient(circle, rgba(50,255,106,0.4) 0%, transparent 70%)'
                  ]
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />

              <img
                src={swagLogo}
                alt="Swag Golf Logo"
                className="w-48 h-48 relative z-10"
              />
            </motion.div>

            {/* Text */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.8 }}
              className="text-center"
            >
              <h1 className="font-display text-3xl font-black uppercase tracking-wider bg-gradient-to-r from-swag-neon-green via-swag-neon-blue to-swag-gold bg-clip-text text-transparent mb-2">
                Swag Golf
              </h1>
              <p className="font-body text-lg text-swag-skull-white/70">
                Pricing Intelligence
              </p>
            </motion.div>

            {/* Loading indicator */}
            <motion.div
              className="flex gap-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
            >
              {[0, 1, 2].map((index) => (
                <motion.div
                  key={index}
                  className="w-3 h-3 rounded-full bg-swag-neon-green"
                  animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: index * 0.2,
                    ease: "easeInOut"
                  }}
                />
              ))}
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
