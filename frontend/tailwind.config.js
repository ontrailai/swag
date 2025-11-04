/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Swag Golf Brand Colors
        'swag-dark': '#0F0F0F',
        'swag-dark-secondary': '#1C1C1C',
        'swag-dark-tertiary': '#2A2A2A',
        'swag-neon-green': '#32FF6A',
        'swag-neon-blue': '#00BFFF',
        'swag-gold': '#D4AF37',
        'swag-magenta': '#FF10F0',
        'swag-purple': '#9D4EDD',
        'swag-skull-white': '#F8F8F8',
      },
      fontFamily: {
        'display': ['Orbitron', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'neon-green': '0 0 20px rgba(50, 255, 106, 0.5)',
        'neon-blue': '0 0 20px rgba(0, 191, 255, 0.5)',
        'neon-gold': '0 0 20px rgba(212, 175, 55, 0.3)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'fade-in': 'fade-in 0.3s ease-in-out',
        'slide-up': 'slide-up 0.3s ease-out',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(50, 255, 106, 0.3)'
          },
          '50%': {
            boxShadow: '0 0 40px rgba(50, 255, 106, 0.6)'
          },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': {
            transform: 'translateY(10px)',
            opacity: '0'
          },
          '100%': {
            transform: 'translateY(0)',
            opacity: '1'
          },
        },
      },
    },
  },
  plugins: [],
}
