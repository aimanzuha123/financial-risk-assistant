/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0f172a',     // Slate 900
          card: '#1e293b',     // Slate 800
          border: '#334155',   // Slate 700
          primary: '#6366f1',  // Indigo 500
          secondary: '#8b5cf6',// Violet 500
          success: '#10b981',  // Emerald 500
          warning: '#f59e0b',  // Amber 500
          danger: '#ef4444',   // Red 500
          accent: '#06b6d4',   // Cyan 500
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
        'neon': '0 0 15px rgba(99, 102, 241, 0.4)',
      }
    },
  },
  plugins: [],
}
