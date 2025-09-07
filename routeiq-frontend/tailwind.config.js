/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // RouteIQ vibrant brand colors from logo
        'brand': {
          'start': '#FF6B35',
          'start-light': '#FF8A5B',
          'start-dark': '#E55A2B',
          'mid': '#D63384',
          'mid-light': '#E85A9B',
          'mid-dark': '#B02A5B',
          'purple': '#8B5CF6',
          'purple-light': '#A78BFA',
          'purple-dark': '#7C3AED',
          'end': '#0EA5E9',
          'end-light': '#38BDF8',
          'end-dark': '#0284C7',
        },
        // Enhanced semantic colors
        'success': {
          DEFAULT: '#10B981',
          light: '#34D399',
          dark: '#059669',
        },
        'warning': {
          DEFAULT: '#F59E0B',
          light: '#FBBF24',
          dark: '#D97706',
        },
        'error': {
          DEFAULT: '#EF4444',
          light: '#F87171',
          dark: '#DC2626',
        },
        'info': {
          DEFAULT: '#3B82F6',
          light: '#60A5FA',
          dark: '#2563EB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        // Main brand gradients
        'brand-gradient': 'linear-gradient(135deg, #FF6B35 0%, #D63384 50%, #0EA5E9 100%)',
        'brand-gradient-horizontal': 'linear-gradient(90deg, #FF6B35 0%, #D63384 50%, #0EA5E9 100%)',
        'brand-gradient-vertical': 'linear-gradient(180deg, #FF6B35 0%, #D63384 50%, #0EA5E9 100%)',
        'brand-gradient-reverse': 'linear-gradient(135deg, #0EA5E9 0%, #D63384 50%, #FF6B35 100%)',
        
        // Subtle gradients
        'brand-subtle': 'linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(14, 165, 233, 0.1) 100%)',
        'brand-light': 'linear-gradient(135deg, #FF8A5B 0%, #E85A9B 50%, #38BDF8 100%)',
        
        // Animated gradient
        'brand-animated': 'linear-gradient(-45deg, #FF6B35, #D63384, #8B5CF6, #0EA5E9)',
        
        // Background gradients
        'page-gradient': 'linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(14, 165, 233, 0.05) 100%)',
        'card-gradient': 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',

        // Semantic gradients used by components
        'success-gradient': 'linear-gradient(135deg, #34D399, #10B981, #059669)',
        'warning-gradient': 'linear-gradient(135deg, #FBBF24, #F59E0B, #D97706)',
        'error-gradient': 'linear-gradient(135deg, #F87171, #EF4444, #DC2626)',
        'info-gradient': 'linear-gradient(135deg, #60A5FA, #3B82F6, #2563EB)',
        'gray-gradient': 'linear-gradient(135deg, #F3F4F6, #E5E7EB, #D1D5DB)',
      },
      boxShadow: {
        'brand': '0 10px 25px -5px rgba(214, 51, 132, 0.25), 0 10px 10px -5px rgba(214, 51, 132, 0.1)',
        'brand-lg': '0 25px 50px -12px rgba(214, 51, 132, 0.25)',
        'success': '0 10px 25px -5px rgba(16, 185, 129, 0.25)',
        'warning': '0 10px 25px -5px rgba(245, 158, 11, 0.25)',
        'error': '0 10px 25px -5px rgba(239, 68, 68, 0.25)',
        'info': '0 10px 25px -5px rgba(59, 130, 246, 0.25)',
      },
      animation: {
        'gradient-x': 'gradient-x 15s ease infinite',
        'gradient-y': 'gradient-y 15s ease infinite',
        'gradient-xy': 'gradient-xy 15s ease infinite',
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'pulse-brand': 'pulse-brand 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'gradient-y': {
          '0%, 100%': {
            'background-size': '400% 400%',
            'background-position': 'center top'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'center center'
          }
        },
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          }
        },
        'gradient-xy': {
          '0%, 100%': {
            'background-size': '400% 400%',
            'background-position': 'left center'
          },
          '25%': {
            'background-size': '400% 400%',
            'background-position': 'right center'
          },
          '50%': {
            'background-size': '400% 400%',
            'background-position': 'center top'
          },
          '75%': {
            'background-size': '400% 400%',
            'background-position': 'center bottom'
          }
        },
        'gradient-shift': {
          '0%, 100%': { 'background-position': '0% 50%' },
          '50%': { 'background-position': '100% 50%' }
        },
        'pulse-brand': {
          '0%, 100%': { 
            'box-shadow': '0 0 0 0 rgba(214, 51, 132, 0.7)' 
          },
          '70%': { 
            'box-shadow': '0 0 0 10px rgba(214, 51, 132, 0)' 
          }
        }
      }
    },
  },
  plugins: [],
}
