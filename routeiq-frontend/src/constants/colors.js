/**
 * RouteIQ Brand Colors
 * Extracted from the official RouteIQ logo gradient
 */
export const BRAND_COLORS = {
  // Orange start - vibrant orange from logo
  start: '#FF6B35',
  startLight: '#FF8A5B',
  startDark: '#E55A2B',
  
  // Pink/Magenta middle - vibrant magenta from logo
  mid: '#D63384',
  midLight: '#E85A9B',
  midDark: '#B02A5B',
  
  // Purple transition - intermediate color
  purple: '#8B5CF6',
  purpleLight: '#A78BFA',
  purpleDark: '#7C3AED',
  
  // Blue end - vibrant blue from logo
  end: '#0EA5E9',
  endLight: '#38BDF8',
  endDark: '#0284C7'
}

// Extended vibrant color palette
export const COLORS = {
  // Brand gradient colors
  brand: BRAND_COLORS,
  
  // Vibrant semantic colors matching brand energy
  success: '#10B981',
  successLight: '#34D399',
  successDark: '#059669',
  
  warning: '#F59E0B',
  warningLight: '#FBBF24',
  warningDark: '#D97706',
  
  error: '#EF4444',
  errorLight: '#F87171',
  errorDark: '#DC2626',
  
  info: '#3B82F6',
  infoLight: '#60A5FA',
  infoDark: '#2563EB',
  
  // Modern neutral colors with slight warmth
  gray: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#E5E5E5',
    300: '#D4D4D4',
    400: '#A3A3A3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717'
  },
  
  // Additional accent colors
  accent: {
    cyan: '#06B6D4',
    teal: '#14B8A6',
    emerald: '#10B981',
    lime: '#84CC16',
    yellow: '#EAB308',
    amber: '#F59E0B',
    rose: '#F43F5E',
    pink: '#EC4899',
    fuchsia: '#D946EF',
    violet: '#8B5CF6',
    indigo: '#6366F1'
  }
}

// Advanced gradient combinations
export const GRADIENTS = {
  // Main brand gradients
  brand: `linear-gradient(135deg, ${BRAND_COLORS.start} 0%, ${BRAND_COLORS.mid} 50%, ${BRAND_COLORS.end} 100%)`,
  brandHorizontal: `linear-gradient(90deg, ${BRAND_COLORS.start} 0%, ${BRAND_COLORS.mid} 50%, ${BRAND_COLORS.end} 100%)`,
  brandVertical: `linear-gradient(180deg, ${BRAND_COLORS.start} 0%, ${BRAND_COLORS.mid} 50%, ${BRAND_COLORS.end} 100%)`,
  brandReverse: `linear-gradient(135deg, ${BRAND_COLORS.end} 0%, ${BRAND_COLORS.mid} 50%, ${BRAND_COLORS.start} 100%)`,
  
  // Subtle gradients with opacity
  brandSubtle: `linear-gradient(135deg, ${BRAND_COLORS.start}15 0%, ${BRAND_COLORS.end}15 100%)`,
  brandLight: `linear-gradient(135deg, ${BRAND_COLORS.startLight} 0%, ${BRAND_COLORS.midLight} 50%, ${BRAND_COLORS.endLight} 100%)`,
  
  // Animated gradients
  brandAnimated: `linear-gradient(-45deg, ${BRAND_COLORS.start}, ${BRAND_COLORS.mid}, ${BRAND_COLORS.purple}, ${BRAND_COLORS.end})`,
  
  // Specific use case gradients
  success: `linear-gradient(135deg, #10B981 0%, #34D399 100%)`,
  warning: `linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)`,
  error: `linear-gradient(135deg, #EF4444 0%, #F87171 100%)`,
  info: `linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)`,
  
  // Background gradients
  pageBackground: `linear-gradient(135deg, ${BRAND_COLORS.start}05 0%, ${BRAND_COLORS.end}05 100%)`,
  cardBackground: `linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)`,
  darkBackground: `linear-gradient(135deg, #1E293B 0%, #334155 100%)`
}

// Shadow colors with brand tints
export const SHADOWS = {
  brand: `0 10px 25px -5px ${BRAND_COLORS.mid}25, 0 10px 10px -5px ${BRAND_COLORS.mid}10`,
  brandLarge: `0 25px 50px -12px ${BRAND_COLORS.mid}25`,
  success: `0 10px 25px -5px #10B98125`,
  warning: `0 10px 25px -5px #F59E0B25`,
  error: `0 10px 25px -5px #EF444425`,
  info: `0 10px 25px -5px #3B82F625`
}

/**
 * Status colors for tickets and system health
 */
export const STATUS_COLORS = {
  ONLINE: COLORS.success,
  OFFLINE: COLORS.error,
  WARNING: COLORS.warning,
  PENDING: COLORS.info,
  
  // Ticket priorities
  HIGH: COLORS.error,
  MEDIUM: COLORS.warning,
  LOW: COLORS.info,
  NORMAL: COLORS.info,
}
