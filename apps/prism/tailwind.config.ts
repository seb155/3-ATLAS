import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        accent: '#6EE7B7',
        surface: '#0B1220',
        panel: '#111827',
      },
      boxShadow: {
        glass: '0 10px 40px -12px rgba(0,0,0,0.45)',
      },
      borderRadius: {
        xl: '1rem',
      },
    },
  },
  plugins: [],
};

export default config;
